from abc import ABC, abstractmethod


class AekaExecutionPhaseBase(ABC):
    def __init__(self, phase_name=None, phase_description=None):
        self.phase_name = phase_name
        self.phase_description = phase_description
        self.result = None
        self.local_context = None
        self.global_context = None
        self.command = None

    @abstractmethod
    def execute_phase(self, input_list: list,*args,**kwargs):
        pass

    @abstractmethod
    def get_result(self):
        pass


    @abstractmethod
    def update_and_return_global_context(self):
        pass

    @abstractmethod
    def setup(self):
        pass
