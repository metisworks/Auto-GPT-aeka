from pathlib import Path

from autogpt.agents.aeka_execution_browse_phase import AekaExecutionBrowsePhase
from autogpt.agents.aeka_execution_phase import AekaExecutionPhaseBase
from autogpt.agents.aeka_input_bounce import AekaInputBouncePhae
from autogpt.config.aeka_execution_plan import ExecutionPlan
from autogpt.core.aeka_core.aekaExecutionContext import AekaExecutionContext


class LinkResearchPlan(ExecutionPlan):
    def __init__(self):
        super().__init__()
        self.search_urls = None
        self.plan_name = "Link browse and research"

    def get_phase(self):
        return self.current_phase

    def current_phase_and_inline(self):
        self.current_phase = next(self.phase_iterator, None)
        return self.current_phase

    def create_from_yaml(self, file: Path | str):
        pass

    def setup_phases(self, phase_list: list[AekaExecutionPhaseBase] = None,
                     goals_list: {int: list[str]} = None,
                     url_list=None,
                     num_result=1):
        if self.phases is None:
            self.phases = []
        if phase_list:
            self.phases += phase_list

        global_context = AekaExecutionContext(context_name="Global Context")

        bounce_phase = AekaInputBouncePhae()
        bounce_phase.setup()
        self.phases.append(bounce_phase)

        # add phase
        goals_for_phase = self.get_goals_for_phase(goals_list, "1")
        browse_executor = AekaExecutionBrowsePhase()
        browse_executor.setup(local_context=AekaExecutionContext(context_name="Local Context"),
                              global_context=global_context, input_goals=goals_for_phase)
        self.phases.append(browse_executor)

        # update iterator
        self.phase_iterator = iter(self.phases)

    @staticmethod
    def get_goals_for_phase(goals_list, index):
        if index in goals_list:
            goals_for_phase = goals_list[index]
        else:
            goals_for_phase = None
        return goals_for_phase


if __name__ == "__main__":
    print("hello")
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
    researchPlan = LinkResearchPlan()
    researchPlan.setup_phases(goals_list=goals)
