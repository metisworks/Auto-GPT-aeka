from autogpt.core.resource.model_providers import MessageRole
from autogpt.llm import Message
from autogpt.models.command import Command


class AekaExecutionContext:
    def __init__(self, context_name, messages=None, context_data_string="", command_history=None):
        self.context_name = context_name
        self.context_data_string = context_data_string
        if messages is None:
            self.messages = []
        if command_history is None:
            self.command_history = []

    def update_context(self, messages: Message = None, context_string: str = None, commands: list[Command] = None):
        pass

    def add_message_to_context(self, prompt: str, role: str):
        message = {
            "role": role,
            "content": prompt
        }
        self.messages.append(message)
        return
