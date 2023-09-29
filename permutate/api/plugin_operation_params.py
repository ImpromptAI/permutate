from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from permutate.api import auth
from permutate.plugin_operation_params import get_plugin_operation_params

# Create a FastAPI router
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


# Define a route to get Plugin Operation Params
@router.get("/plugin-operation-params")
def plugin_operation_params(
    openplugin_manifest_url: str,
    api_key: APIKey = Depends(auth.get_api_key),
):
    try:
        # Read data from a JSON file
        return get_plugin_operation_params(openplugin_manifest_url)
    except Exception as e:
        print(e)
        # Return a JSON response with a 500 status code in case of an exception
        return JSONResponse(
            status_code=500,
            content={"message": "Failed to get Plugin Operation Params"},
        )
