from autogpt.agents.aeka_execution_phase import AekaExecutionPhaseBase
from autogpt.agents.utils.util_method import execute_prompt_chat
from autogpt.commands.web_search import web_search
from autogpt.core.aeka_core.aekaExecutionContext import AekaExecutionContext
from autogpt.logs import logger
import json


class AekaInputBouncePhae(AekaExecutionPhaseBase):
    def __init__(self):
        super().__init__()
        self.phase_name = "input bounce phase"
        self.phase_description = "Phase for doing a search"
        self.command = None
        self.credentials = None
        self.num_result = 1

    def setup(self):
        pass

    def execute_phase(self, input_list: list, *args, **kwargs):
        """

        Args:
            *args:
            **kwargs:
            input_list: list of input goals

        Returns:

        """
        self.result = input_list
        return input_list

    def get_result(self):
        return self.result

    def update_and_return_global_context(self):
        pass
