from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey
from permutate.api import auth
import json
from typing import Optional, List
from itertools import combinations

router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/llm-permutations")
def get_llm_permutations(
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        api_key: APIKey = Depends(auth.get_api_key)
):
    try:
        with open('permutate/templates/llm_permutations.json', 'r') as json_file:
            data = json.load(json_file)
            conditions = []
            if provider:
                conditions.append(lambda obj: obj["provider"] == provider)
            if model_name:
                conditions.append(lambda obj: obj["model_name"] == model_name)
            if conditions:
                data = list(
                    filter(lambda obj: all(cond(obj) for cond in conditions), data))
            return data
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,
                            content={"message": "Failed to get LLM Permutations"})


@router.get("/plugin-group-permutations")
def get_plugin_group_permutations(
        request: Request,
        api_key: APIKey = Depends(auth.get_api_key)
):
    try:
        plugins = request.query_params.getlist('plugin_manifest')
        if len(plugins) == 0:
            return []
        all_combinations = []
        index = 1
        for r in range(1, len(plugins) + 1):
            for pl in list(combinations(plugins, r)):
                all_combinations.append({
                    "name": f"Plugin Group {index}",
                    "plugins": [{"manifest_url": k} for k in pl]

                })
                index += 1
        return all_combinations
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,
                            content={"message": "Failed to run plugin"})


@router.get("/tool-selector-permutations")
def get_tool_selector_permutations(
        provider: Optional[str] = None,
        pipeline_name: Optional[str] = None,
        api_key: APIKey = Depends(auth.get_api_key)
):
    try:
        with open('permutate/templates/tool_selector_permutations.json',
                  'r') as json_file:
            data = json.load(json_file)
            conditions = []
            if provider:
                conditions.append(lambda obj: obj["provider"] == provider)
            if pipeline_name:
                conditions.append(lambda obj: obj["pipeline_name"] == pipeline_name)
            if conditions:
                data = list(
                    filter(lambda obj: all(cond(obj) for cond in conditions), data))
            return data
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,
                            content={
                                "message": "Failed to get Tool Selector Permutations"})
