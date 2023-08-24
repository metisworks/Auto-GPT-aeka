from autogpt.agents.aeka_execution_phase import AekaExecutionPhaseBase
from autogpt.commands.web_search import web_search
from autogpt.core.aeka_core.aekaExecutionContext import AekaExecutionContext
from autogpt.llm.base import ResponseMessageDict
from autogpt.llm.providers.openai import create_chat_completion
from autogpt.logs import logger
import json

GPT_4_MODEL = "gpt-4"
GPT_3_MODEL = "gpt-3.5-turbo"


class AekaExecutionSearchPhase(AekaExecutionPhaseBase):
    def __init__(self):
        super().__init__()
        self.phase_name = "Search_Execution"
        self.phase_description = "Phase for doing a search"
        self.command = web_search
        self.credentials = None

    def setup(self, local_context: AekaExecutionContext = None, global_context: AekaExecutionContext = None,
              credentials: dict = None):
        self.local_context = local_context
        self.global_context = global_context
        self.credentials = credentials

    def execute_phase(self, input_list: list, *args, **kwargs):
        '''

        Args:
            *args:
            **kwargs:
            input_list: list of input goals

        Returns:

        '''

        # 1.generate search terms
        #   1.1 generate search prompt
        execution_messages = []
        if self.global_context:
            execution_messages += self.global_context.messages

        if self.local_context:
            execution_messages += self.local_context.messages

        prompt = f"For searching the web for the topic as {' '.join(input_list)}. Please generate a concise " \
                 f" search query that can be fed to a search engine."
        message = {
            "role": "user",
            "content": prompt
        }
        self.local_context.messages.append(message)
        execution_messages.append(message)

        #   1.2 call open ai
        search_term = execute_prompt_chat(execution_messages)

        # 2. search
        search_result = self.command(search_term, None)
        search_result_obj = json.loads(search_result)
        print(f" { search_result = }")
        for res_obj in search_result_obj:
            print(f"{ res_obj = }")
        self.result = search_result_obj

    def get_result(self):
        return self.result

    def update_and_return_global_context(self):
        pass


def execute_prompt_chat(messages, **kwargs):
    chat_completion_kwargs = {
        "model": GPT_3_MODEL,
        "temperature": 0,
        "api_key": "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",
        "api_base": None,
        "organization": None
    }
    results = create_chat_completion(messages=messages,**chat_completion_kwargs)
    print(f"{results = }")
    if hasattr(results, "error"):
        logger.error(results.error)
        raise RuntimeError(results.error)
    first_message: ResponseMessageDict = results.choices[0].message
    content: str | None = first_message.get("content")
    content = content.strip('\\').strip('\"')
    return content


if __name__ == "__main__":
    context = AekaExecutionContext(context_name="Local Context")
    global_context = AekaExecutionContext(context_name="Global Context")
    global_context.add_message_to_context("Think of yourself as a research analyst", "user")
    exec_phase = AekaExecutionSearchPhase()
    exec_phase.setup(local_context=context, global_context=global_context)
    goals = ["Find the luxury car market  size in usd in india for 2023",
             "Please prioritise govt agencies pdf reports and reputed statistic sites."]
    exec_phase.execute_phase(input_list=goals)
    print("hello")
