import traceback
from typing import Any

import requests
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from permutate import (
    Config,
    JobRequest,
    Permutation,
    Plugin,
    PluginGroup,
    Runner,
    TestCase,
)
from permutate.api import auth

# Create a FastAPI router
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


# Define a route to start a permutate job
@router.post("/start-job")
def start_job(
    job_request: JobRequest, api_key: APIKey = Depends(auth.get_api_key)
) -> Any:
    try:
        # Create a Runner instance
        runner = Runner()
        # Start the job request and return the result
        return runner.start_request(
            job_request, output_directory=None, save_to_html=False, save_to_csv=False
        )
    except Exception as e:
        print(e)
        traceback.print_exc()
        # Return a JSON response with a 500 status code in case of an exception
        return JSONResponse(
            status_code=500, content={"message": "Failed to run plugin"}
        )


@router.post("/start-job-s3")
def start_job_s3(
    permutation_test_url: str, api_key: APIKey = Depends(auth.get_api_key)
) -> Any:
    try:
        runner = Runner()
        test_json = requests.get(permutation_test_url).json()
        job_request = JobRequest(**test_json)
        return runner.start_request(
            job_request, output_directory=None, save_to_html=False, save_to_csv=False
        )
    except Exception as e:
        print(e)
        traceback.print_exc()
        # Return a JSON response with a 500 status code in case of an exception
        return JSONResponse(
            status_code=500, content={"message": "Failed to run plugin"}
        )


# Define a route for interactive job runs
@router.post("/interactive-run")
def start_job_interactive(  # noqa: F811
    config: Config,
    plugin: Plugin,
    plugin_group: PluginGroup,
    permutation: Permutation,
    test_case: TestCase,
    api_key: APIKey = Depends(auth.get_api_key),
) -> Any:
    try:
        # Create a JobRequest object using the provided parameters
        job_request = JobRequest(
            version="1.0",
            name="interactive-run",
            config=config,
            test_plugin=plugin,
            plugin_groups=[plugin_group],
            permutations=[permutation],
            test_cases=[test_case],
        )
        # Create a Runner instance
        runner = Runner()
        # Start the job request and return the result
        return runner.start_request(
            job_request, output_directory=None, save_to_html=False, save_to_csv=False
        )
    except Exception as e:
        print(e)
        # Return a JSON response with a 500 status code in case of an exception
        return JSONResponse(
            status_code=500, content={"message": "Failed to run plugin"}
        )
