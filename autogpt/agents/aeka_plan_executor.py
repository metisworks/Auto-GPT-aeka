# Create a plan executor
import uuid
from abc import ABC, abstractmethod

from autogpt.config.aeka_execution_plan import ExecutionPlan
from autogpt.agents.aeka_execution_phase import AekaExecutionPhaseBase


class AekaPlanExecutor(ABC):
    def __init__(self, name: str):
        self.id = uuid.uuid4()
        self.name = name
        self.execution_plans = None
        self.messages = []
        self.long_term_context = None

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def setup_execution_plans(self, execution_plans: list[ExecutionPlan]):
        pass


if __name__ == "__main__":
    print("Hello")

