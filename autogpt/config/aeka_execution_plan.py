import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from autogpt.agents.aeka_execution_phase import AekaExecutionPhaseBase


class ExecutionPlan(ABC):
    def __init__(self, plan_name=None):
        self.plan_name = plan_name
        self.phases = None
        self.current_phase = None

    @abstractmethod
    def get_phase(self):
        pass

    @abstractmethod
    def next_phase(self):
        pass

    @abstractmethod
    def create_from_yaml(self, file: Path | str):
        pass

    @abstractmethod
    def setup_phases(self, phase_list: list[AekaExecutionPhaseBase]):
        pass
