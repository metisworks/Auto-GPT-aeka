# Create a plan executor
import uuid
from abc import ABC, abstractmethod

from autogpt.config.aeka_execution_plan import ExecutionPlan
from autogpt.agents.aeka_execution_phase import AekaExecutionPhaseBase
from autogpt.config.gpt_browse_research_plan import GptBrowseResearchPlan


class AekaPlanExecutor(ABC):
    def __init__(self, name: str):
        self.id = uuid.uuid4()
        self.name = name
        self.execution_plan: ExecutionPlan = None
        self.messages = []
        self.long_term_context = None

    def execute(self):
        if not self.execution_plan:
            raise Exception("No execution Plan")

        inp_to_next_phase = None
        while self.execution_plan.current_phase_and_inline():
            current_phase: AekaExecutionPhaseBase = self.execution_plan.current_phase
            current_phase.execute_phase(inp_to_next_phase)
            inp_to_next_phase = current_phase.get_result()

        return inp_to_next_phase

    def setup_execution_plans(self, execution_plan: ExecutionPlan):
        self.execution_plan = execution_plan


if __name__ == "__main__":
    print("Hello")
    # create execution plan
    goals = {
        "0": [
            "Find the luxury car market  size in usd in india for 2023",
            "Please prioritise govt agencies reports and reputed statistic sites."
        ],
        "1": [
            "Whats the luxury automobile market in India for 2023",
            "Please provide the answer as JSON with keys as year of sales, market size, CAGR"
        ],

    }
    s_b_plan = GptBrowseResearchPlan()
    s_b_plan.setup_phases(goals_list=goals)

    executor = AekaPlanExecutor("research executor")
    executor.setup_execution_plans(s_b_plan)
    executor.execute()

