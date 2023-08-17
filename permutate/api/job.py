from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey
from permutate.api import auth
from permutate import JobRequest, Runner, Plugin, PluginGroup, Permutation, TestCase, \
    Config

router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/start-job")
def start_job(
        job_request: JobRequest,
        api_key: APIKey = Depends(auth.get_api_key)
):
    try:
        runner = Runner()
        return runner.start_request(job_request, output_directory=None,
                                    save_to_html=False, save_to_csv=False)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,
                            content={"message": "Failed to run plugin"})


@router.post("/interactive-run")
def start_job(
        config: Config,
        plugin: Plugin,
        plugin_group: PluginGroup,
        permutation: Permutation,
        test_case: TestCase,
        api_key: APIKey = Depends(auth.get_api_key)
):
    try:
        job_request = JobRequest(
            version="1.0",
            name="interactive-run",
            config=config,
            test_plugin=plugin,
            plugin_groups=[plugin_group],
            permutations=[permutation],
            test_cases=[test_case]
        )
        runner = Runner()
        return runner.start_request(job_request, output_directory=None,
                                    save_to_html=False, save_to_csv=False)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,
                            content={"message": "Failed to run plugin"})
