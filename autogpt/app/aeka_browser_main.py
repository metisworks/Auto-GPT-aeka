import os.path
import sys
from pathlib import Path
from types import FrameType
import signal
from typing import Optional
import re
from colorama import Fore, Style

from autogpt.agents import Agent
from autogpt.agents.utils.exceptions import InvalidAgentResponseError
from autogpt.config import ConfigBuilder, Config, AIConfig
from autogpt.llm.api_manager import ApiManager
from autogpt.logs import logger
import logging
from autogpt.app.configurator import create_config
from autogpt.memory.vector import get_memory
from autogpt.models.command_registry import CommandRegistry
from autogpt.plugins import scan_plugins
from autogpt.prompts.prompt import DEFAULT_TRIGGERING_PROMPT
from autogpt.workspace import Workspace


def run_main(debug: bool,
             working_directory: Path,
             workspace_directory: str | Path,
             ai_goals: tuple[str] = tuple(),
             cycle_count=5):
    # Configure logging before we do anything else.
    logger.set_level(logging.DEBUG if debug else logging.INFO)

    config = ConfigBuilder.build_config_from_env(workdir=working_directory)
    prompt_settings_file = Path("./../../prompt_settings.yaml")
    # manually set the config values
    create_config(
        config=config,
        continuous=False,
        continuous_limit=0,
        ai_settings_file="",
        prompt_settings_file="./../../prompt_settings.yaml",
        skip_reprompt=True,
        speak=False,
        debug=debug,
        gpt3only=True,
        gpt4only=False,
        memory_type="json_file",
        browser_name=config.selenium_web_browser,
        allow_downloads=False,
        skip_news=True,
    )

    if config.continuous_mode:
        for line in get_legal_warning().split("\n"):
            logger.warn(markdown_to_ansi_style(line), "LEGAL:", Fore.RED)

    config.workspace_path = Workspace.init_workspace_directory(
        config, workspace_directory
    )

    # HACK: doing this here to collect some globals that depend on the workspace.
    config.file_logger_path = Workspace.build_file_logger_path(config.workspace_path)

    # config.plugins = scan_plugins(config, config.debug_mode)

    # Create a CommandRegistry instance and scan default folder
    new_command_categories = ["autogpt.commands.web_search",
                              "autogpt.commands.web_selenium",
                              "autogpt.commands.execute_code",
                              "autogpt.commands.file_operations",
                              ]
    command_registry = CommandRegistry.with_command_modules(new_command_categories, config)

    ai_config = construct_main_ai_config(
        config,
        name="Market researcher",
        role="Research financial data",
        goals=ai_goals,
    )
    ai_config.command_registry = command_registry
    memory = get_memory(config)
    memory.clear()
    logger.typewriter_log(
        "Using memory of type:", Fore.GREEN, f"{memory.__class__.__name__}"
    )
    logger.typewriter_log("Using Browser:", Fore.GREEN, config.selenium_web_browser)

    agent = Agent(
        memory=memory,
        command_registry=command_registry,
        triggering_prompt=DEFAULT_TRIGGERING_PROMPT,
        ai_config=ai_config,
        config=config,
    )
    results = run_research(agent, cycle_count)
    return results[-1], results


def run_research(agent: Agent, cycle_count):
    config = agent.config
    ai_config = agent.ai_config
    logger.debug(f"{ai_config.ai_name} System Prompt: {agent.system_prompt}")

    if cycle_count:
        cycle_budget = cycles_remaining = cycle_count
    else:
        cycle_budget = cycles_remaining = _get_cycle_budget(
            config.continuous_mode, config.continuous_limit
        )

    def graceful_agent_interrupt(signum: int, frame: Optional[FrameType]) -> None:
        nonlocal cycle_budget, cycles_remaining
        logger.typewriter_log(
            "Interrupt signal received. Stopping Auto-GPT immediately.",
            Fore.RED,
        )
        sys.exit()

    # Set up an interrupt signal for the agent.
    signal.signal(signal.SIGINT, graceful_agent_interrupt)

    #########################
    # Application Main Loop #
    #########################

    # Keep track of consecutive failures of the agent
    consecutive_failures = 0
    all_results = []
    current_cycle = 0
    loop_cycle = 0
    browse_cycle = 0

    while cycles_remaining > 0:
        current_cycle += 1
        logger.debug(f"Cycle budget: {cycle_budget}; remaining: {cycles_remaining}")

        ########
        # Plan #
        ########
        # Have the agent determine the next action to take.
        try:
            command_name, command_args, assistant_reply_dict = agent.think()
        except InvalidAgentResponseError as e:
            logger.warn(f"The agent's thoughts could not be parsed: {e}")
            consecutive_failures += 1
            if consecutive_failures >= 3:
                logger.error(
                    f"The agent failed to output valid thoughts {consecutive_failures} "
                    "times in a row. Terminating..."
                )
                sys.exit()
            continue

        logger.typewriter_log("MAINTAINER: ", Fore.MAGENTA, f" \n {command_name = } | {command_args = } | { assistant_reply_dict}")
        result = agent.execute(command_name, command_args, "")

        if result.status == "success":
            logger.typewriter_log("SYSTEM: ", Fore.YELLOW, result.results)
            all_results.append(result)

        elif result.status == "error":
            logger.warn(
                f"Command -->> {command_name} returned an error: {result.error or result.reason}"
            )
        if command_name != "web_search" and command_name != "browse_website" :
            loop_cycle += 1
            cycles_remaining -= 1
            if command_name == "browse_website":
                browse_cycle += 1

        logger.typewriter_log(f"MAINTAINER", Fore.MAGENTA, f"{current_cycle = }   | {cycles_remaining = }")


        if current_cycle > 15 or loop_cycle > 10:
            logger.warn( f"Exceeded 20 cycles or loop cycle SHUTTING DOWN")
            break

    return all_results


# ---------------------------
def construct_main_ai_config(
        config: Config,
        name: Optional[str] = None,
        role: Optional[str] = None,
        goals: tuple[str] = tuple(),
) -> AIConfig:
    """Construct the prompt for the AI to respond to

    Returns:
        str: The prompt string
    """
    ai_config = AIConfig.load(config.workdir / config.ai_settings_file)

    # TODO remove hardcoded budget limit
    ai_config.api_budget = ai_config.api_budget if ai_config.api_budget <= 0 else 0.02

    # Apply overrides
    if name:
        ai_config.ai_name = name
    if role:
        ai_config.ai_role = role
    if goals:
        ai_config.ai_goals = list(goals)

    if (
            all([name, role, goals])
            or config.skip_reprompt
            and all([ai_config.ai_name, ai_config.ai_role, ai_config.ai_goals])
    ):
        logger.typewriter_log("Name :", Fore.GREEN, ai_config.ai_name)
        logger.typewriter_log("Role :", Fore.GREEN, ai_config.ai_role)
        logger.typewriter_log("Goals:", Fore.GREEN, f"{ai_config.ai_goals}")
        logger.typewriter_log(
            "API Budget:",
            Fore.GREEN,
            "infinite" if ai_config.api_budget <= 0 else f"${ai_config.api_budget}",
        )
    else:
        raise Exception(f"Incorrect config given {ai_config}")

    if any([not ai_config.ai_name, not ai_config.ai_role, not ai_config.ai_goals]):
        raise Exception(f"incomplete ai config: {ai_config}")

    if config.restrict_to_workspace:
        logger.typewriter_log(
            "NOTE:All files/directories created by this agent can be found inside its workspace at:",
            Fore.YELLOW,
            f"{config.workspace_path}",
        )
    # set the total api budget
    api_manager = ApiManager()
    api_manager.set_total_budget(ai_config.api_budget)

    # Agent Created, print message
    logger.typewriter_log(
        ai_config.ai_name,
        Fore.LIGHTBLUE_EX,
        "has been created with the following details:",
        speak_text=False,
    )

    # Print the ai_config details
    # Name
    logger.typewriter_log("Name:", Fore.GREEN, ai_config.ai_name, speak_text=False)
    # Role
    logger.typewriter_log("Role:", Fore.GREEN, ai_config.ai_role, speak_text=False)
    # Goals
    logger.typewriter_log("Goals:", Fore.GREEN, "", speak_text=False)
    for goal in ai_config.ai_goals:
        logger.typewriter_log("-", Fore.GREEN, goal, speak_text=False)

    return ai_config


# ---------

def _get_cycle_budget(continuous_mode: bool, continuous_limit: int) -> int | float:
    # Translate from the continuous_mode/continuous_limit config
    # to a cycle_budget (maximum number of cycles to run without checking in with the
    # user) and a count of cycles_remaining before we check in..
    if continuous_mode:
        cycle_budget = continuous_limit if continuous_limit else 10
    else:
        cycle_budget = 1

    return cycle_budget


# -------------
def markdown_to_ansi_style(markdown: str):
    ansi_lines: list[str] = []
    for line in markdown.split("\n"):
        line_style = ""

        if line.startswith("# "):
            line_style += Style.BRIGHT
        else:
            line = re.sub(
                r"(?<!\*)\*(\*?[^*]+\*?)\*(?!\*)",
                rf"{Style.BRIGHT}\1{Style.NORMAL}",
                line,
            )

        if re.match(r"^#+ ", line) is not None:
            line_style += Fore.CYAN
            line = re.sub(r"^#+ ", "", line)

        ansi_lines.append(f"{line_style}{line}{Style.RESET_ALL}")
    return "\n".join(ansi_lines)


# --------------
def get_legal_warning() -> str:
    legal_text = """
## DISCLAIMER AND INDEMNIFICATION AGREEMENT
### PLEASE READ THIS DISCLAIMER AND INDEMNIFICATION AGREEMENT CAREFULLY BEFORE USING THE AUTOGPT SYSTEM. BY USING THE AUTOGPT SYSTEM, YOU AGREE TO BE BOUND BY THIS AGREEMENT.

## Introduction
AutoGPT (the "System") is a project that connects a GPT-like artificial intelligence system to the internet and allows it to automate tasks. While the System is designed to be useful and efficient, there may be instances where the System could perform actions that may cause harm or have unintended consequences.

## No Liability for Actions of the System
The developers, contributors, and maintainers of the AutoGPT project (collectively, the "Project Parties") make no warranties or representations, express or implied, about the System's performance, accuracy, reliability, or safety. By using the System, you understand and agree that the Project Parties shall not be liable for any actions taken by the System or any consequences resulting from such actions.

## User Responsibility and Respondeat Superior Liability
As a user of the System, you are responsible for supervising and monitoring the actions of the System while it is operating on your
behalf. You acknowledge that using the System could expose you to potential liability including but not limited to respondeat superior and you agree to assume all risks and liabilities associated with such potential liability.

## Indemnification
By using the System, you agree to indemnify, defend, and hold harmless the Project Parties from and against any and all claims, liabilities, damages, losses, or expenses (including reasonable attorneys' fees and costs) arising out of or in connection with your use of the System, including, without limitation, any actions taken by the System on your behalf, any failure to properly supervise or monitor the System, and any resulting harm or unintended consequences.
            """
    return legal_text


# --------------
def main():
    # work_dir = os.path.dirname('./../../auto_gpt_workspace/')
    work_dir = Path('./../../auto_gpt_workspace/')
    print(work_dir)
    for a in os.walk(work_dir):
        print(a)
    ai_goals = ("Present an overview of the luxury automobile market India in 2023", " present data as json ","do not write to any file")

    fin_res, results = run_main(False, work_dir, work_dir, ai_goals, 2)
    print(f" Fin {fin_res = } and \n {results =}")


if __name__ == "__main__":
    main()
