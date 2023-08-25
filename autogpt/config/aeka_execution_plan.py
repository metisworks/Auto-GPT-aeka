import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from autogpt.agents.aeka_execution_phase import AekaExecutionPhaseBase


class ExecutionPlan(ABC):
    def __init__(self, plan_name=None):
        self.plan_name = plan_name
        self.phases = None
        self.current_phase = None
        self.phase_iterator = None

    @abstractmethod
    def get_phase(self):
        pass

    @abstractmethod
    def current_phase_and_inline(self):
        pass

    @abstractmethod
    def create_from_yaml(self, file: Path | str):
        pass

    @abstractmethod
    def setup_phases(self, phase_list: list[AekaExecutionPhaseBase] = None, goals_list: {int: list[str]} = None):
        pass
