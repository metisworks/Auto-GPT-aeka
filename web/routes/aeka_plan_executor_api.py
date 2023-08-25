from fastapi import APIRouter, Body
from autogpt.agents.aeka_plan_executor import AekaPlanExecutor
from typing import List, Annotated

from autogpt.config.gpt_browse_research_plan import GptBrowseResearchPlan

router = APIRouter(prefix="/vulcan/aeka_agent")
plan_executor = AekaPlanExecutor("Research Executor")


@router.post(path="/srb", tags=["aeka_autogpt"])
def execute_srb_request(
        search_goals: Annotated[List[str], Body()],
        research_goals: Annotated[List[str], Body()]
):
    """

    Args:
        search_goals:
        research_goals:

    Returns:

    """
    search_goal_inp = {
        "0": search_goals,
        "1": research_goals
    }
    s_b_plan = GptBrowseResearchPlan()
    s_b_plan.setup_phases(goals_list=search_goal_inp)
    plan_executor.setup_execution_plans(s_b_plan)
    results = plan_executor.execute()
    del s_b_plan
    return results


