import json
from pathlib import Path

from autogpt.agents.aeka_execution_phase import AekaExecutionPhaseBase
from autogpt.agents.aeka_execution_search_phase import AekaExecutionSearchPhase
from autogpt.commands.web_selenium import browse_website
from autogpt.config import ConfigBuilder, Config
from autogpt.core.aeka_core.aekaExecutionContext import AekaExecutionContext

GPT_4_MODEL = "gpt-4"
GPT_3_MODEL = "gpt-3.5-turbo"


class AekaExecutionBrowsePhase(AekaExecutionPhaseBase):
    def __init__(self):
        super().__init__()
        self.phase_name = "Browse sites"
        self.phase_description = "Phase for doing a search"
        self.command = browse_website
        self.credentials = None
        # create config
        # set the work dir
        path = Path("./../../auto_gpt_workspace")
        self.config = ConfigBuilder().build_config_from_env(path)
        self.config.memory_backend = "no_memory"
        self.config.workspace_path = path

    def execute_phase(self, input_list: list, *args, **kwargs):
        '''

        Args:
            *args:
            **kwargs:
            input_list: list of urls

        Returns:

        '''
        print(f" {input_list = }")
        goals_list = kwargs.get("goals", None)
        if not goals_list or not isinstance(goals_list, list):
            raise Exception("Couldn't find goals")

        goal_string = ".".join(goals_list)
        print(f" {goal_string = } ")
        answer_list = []

        for result_details in input_list:
            print(f"{ result_details = }")
            website_url = result_details['href']
            browse_answer = self.command(url=website_url,
                                         question=goal_string,
                                         llm_name=GPT_3_MODEL,
                                         config=self.config)
            answer = {
                "answer": json.loads(browse_answer),
                "link": website_url
            }
            answer_list.append(answer)
            print(f"{browse_answer = }")

        print(f" { answer_list = }")
        self.result = answer_list
        return answer_list

    def get_result(self):
        return self.result

    def update_and_return_global_context(self):
        pass

    def setup(self, local_context=None, global_context=None, credentials=None):
        self.local_context = local_context
        self.global_context = global_context
        self.credentials = credentials
        pass


if __name__ == "__main__":
    context = AekaExecutionContext(context_name="Local Context")
    global_context = AekaExecutionContext(context_name="Global Context")
    global_context.add_message_to_context("Think of yourself as a research analyst", "user")
    exec_phase = AekaExecutionSearchPhase()
    exec_phase.setup(local_context=context, global_context=global_context)
    goals = ["Find the luxury car market  size in usd in india for 2023",
             "Please prioritise govt agencies reports and reputed statistic sites."]
    exec_phase.execute_phase(input_list=goals)
    print("hello")
    browse_executor = AekaExecutionBrowsePhase()
    res = exec_phase.get_result()
    context = AekaExecutionContext(context_name="Local Context")
    goals = ["Whats the luxury automobile market in India for 2023",
             "Please provide the answer as JSON with keys as year, market size, CAGR"]
    browse_executor.setup(local_context=context, global_context=global_context)
    browse_executor.execute_phase(res, goals=goals)
