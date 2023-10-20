from autogpt.agents.aeka_execution_phase import AekaExecutionPhaseBase
from autogpt.agents.utils.util_method import execute_prompt_chat
from autogpt.commands.web_search import web_search
from autogpt.commands.apify_google_search import get_serp_results
from autogpt.core.aeka_core.aekaExecutionContext import AekaExecutionContext
from autogpt.logs import logger
import json
from apify_client import ApifyClient

class AekaExecutionSerpPhase(AekaExecutionPhaseBase):
    def __init__(self):
        super().__init__()
        self.phase_name = "Search_Execution"
        self.phase_description = "Phase for doing a search"
        self.command = get_serp_results
        self.credentials = None
        self.num_result =1

    def setup(self, local_context: AekaExecutionContext = None, global_context: AekaExecutionContext = None,
              input_goals: [str] = None, num_result:int = 1 ):
        self.local_context = local_context
        self.global_context = global_context
        self.input_goals = input_goals
        self.num_result = num_result

    def execute_phase(self, input_list: list,*args, **kwargs):
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

        if input_list:
            self.input_goals = input_list

        prompt = f"For searching the web for the topic as {' '.join(self.input_goals)}. Please generate a concise " \
                 f" search query that can be fed to a search engine."
        message = {
            "role": "user",
            "content": prompt
        }
        print()
        self.local_context.messages.append(message)
        execution_messages.append(message)

        #   1.2 call open ai
        search_term = execute_prompt_chat(execution_messages)
        print(f" ---> ST {search_term = }")
        # 2. search
        # add token here
        apf_tok = ""
        client = ApifyClient(apf_tok)

        search_result = self.command(client,search_term,self.num_result,1)
        res_list = []
        for res in search_result['results'][0]['organicResults']:
            res['href'] = res['url']
            res_list.append(res)

        print(f"{res_list = }")
        self.result = res_list

    def get_result(self):
        return self.result

    def update_and_return_global_context(self):
        pass


if __name__ == "__main__":
    context = AekaExecutionContext(context_name="Local Context")
    global_context = AekaExecutionContext(context_name="Global Context")
    global_context.add_message_to_context("Think of yourself as a research analyst", "user")
    exec_phase = AekaExecutionSerpPhase()
    exec_phase.setup(local_context=context, global_context=global_context)
    goals = ["Find the luxury car market  size in usd in india for 2023"]
        # ,
        #      "Please prioritise govt agencies pdf reports and reputed statistic sites."]
    exec_phase.execute_phase(input_list=goals)
