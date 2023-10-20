import json
import time
import uuid

# from web import result_db
from fastapi import APIRouter, Body, BackgroundTasks, Request
from autogpt.agents.aeka_plan_executor import AekaPlanExecutor
from typing import List, Annotated

from autogpt.config.gpt_browse_research_plan import GptBrowseResearchPlan
from autogpt.config.gpt_serp_browse_research_plan import GptSerpBrowseResearchPlan

from mongo_cache.result_obj_db_operations import ResultObjDbOperation

router = APIRouter(prefix="/vulcan/aeka_agent")
# db_ops = result_db
db_ops = ResultObjDbOperation("mongodb+srv://metisadmin:metisdata2023@cluster1.616znwm.mongodb.net/", "metis")


@router.post(path="/initiate_srb", tags=["aeka_autogpt"])
async def execute_srb_request(
        search_goals: Annotated[List[str], Body()],
        research_goals: Annotated[List[str], Body()],
        bg_task: BackgroundTasks,
        num_results: Annotated[int, Body()] = 1
):
    """

    Args:
        num_results:
        request:
        bg_task:
        search_goals:
        research_goals:

    Returns:

    """
    search_goal_inp = {
        "0": search_goals,
        "1": research_goals
    }
    run_id = str(uuid.uuid4())
    bg_task.add_task(api_async_fn, run_id, search_goal_inp, num_results)
    # results = api_execution(search_goal_inp)
    return run_id


@router.post(path="/synchronous_srb", tags=["aeka_autogpt"])
async def sync_execute_srb_request(
        search_goals: Annotated[List[str], Body()],
        research_goals: Annotated[List[str], Body()],
        bg_task: BackgroundTasks,
        num_results: Annotated[int, Body()] = 6
):
    search_goal_inp = {
        "0": search_goals,
        "1": research_goals
    }
    run_id = str(uuid.uuid4())
    results = sync_api_execution_fn(run_id, search_goal_inp, num_results)
    return results

@router.post(path="/synchronous_gsrp_rb", tags=["aeka_autogpt"])
async def sync_execute_srb_request(
        search_goals: Annotated[List[str], Body()],
        research_goals: Annotated[List[str], Body()],
        bg_task: BackgroundTasks,
        num_results: Annotated[int, Body()] = 6
):
    search_goal_inp = {
        "0": search_goals,
        "1": research_goals
    }
    run_id = str(uuid.uuid4())
    results = sync_serp_api_execution_fn(run_id, search_goal_inp, num_results)
    return results



def api_execution(search_goal_inp, num_result=1):
    plan_executor = AekaPlanExecutor("Research Executor")
    print("Plan executor")
    s_b_plan = GptBrowseResearchPlan()
    s_b_plan.setup_phases(goals_list=search_goal_inp, num_result=num_result)
    plan_executor.setup_execution_plans(s_b_plan)
    results = plan_executor.execute()
    del s_b_plan
    del plan_executor
    return results


def serp_api_execution(search_goal_inp, num_result=1):
    plan_executor = AekaPlanExecutor("Research Executor")
    print("Plan executor")
    s_b_plan = GptSerpBrowseResearchPlan()
    s_b_plan.setup_phases(goals_list=search_goal_inp, num_result=num_result)
    plan_executor.setup_execution_plans(s_b_plan)
    results = plan_executor.execute()
    del s_b_plan
    del plan_executor
    return results


async def api_async_fn(run_id, inp, num_results=1):
    print(f"Processing for {run_id}")
    print(f"Goals {inp}")
    results = api_execution(inp, num_result=num_results)
    # local_memory_map[run_id] = await get_request(inp, headers)
    result_dict = {"goal_results": results}
    db_ops.add_result_obj(run_id=run_id, input_goals=inp, result=result_dict)
    return


def sync_api_execution_fn(run_id, inp, num_results=1):
    results = api_execution(inp, num_result=num_results)
    # local_memory_map[run_id] = await get_request(inp, headers)
    result_dict = {"goal_results": results}
    db_ops.add_result_obj(run_id=run_id, input_goals=inp, result=result_dict)
    return {'run_id': run_id, 'input_goals': inp, 'result': result_dict}


def sync_serp_api_execution_fn(run_id, inp, num_results=1):
    results = serp_api_execution(inp, num_result=num_results)
    # local_memory_map[run_id] = await get_request(inp, headers)
    result_dict = {"goal_results": results}
    db_ops.add_result_obj(run_id=run_id, input_goals=inp, result=result_dict)
    return {'run_id': run_id, 'input_goals': inp, 'result': result_dict}


@router.get("/get_srb_result/{run_id}")
async def get_output(run_id: str):
    result_obj = db_ops.get_result_obj(run_id)
    if not result_obj:
        return "No such execution"
    return json.loads(result_obj.to_json())
