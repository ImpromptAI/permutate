import os
from typing import Any

from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

# Create an empty set to store API keys
keys = set()
# Load environment variables from a .env file
load_dotenv()
# Load additional environment variables from a specified path if provided
if os.environ.get("USER_ACCESS_KEYS_FILE_PATH") is not None:
    load_dotenv(os.environ.get("USER_ACCESS_KEYS_FILE_PATH"))
# Iterate through environment variables to find and store user access keys
for key in os.environ:
    if key.startswith("user_access_key_"):
        keys.add(os.environ[key])
# Define an APIKeyHeader instance for API key validation
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


# Define a function to get and validate the API key
async def get_api_key(api_key_header: str = Security(api_key_header)) -> Any:
    # If no keys are set up, allow any API key
    if len(keys) == 0:
        return api_key_header
    if api_key_header in keys:
        return api_key_header
    else:
        # Raise an HTTPException with a 403 Forbidden status code if the API key is not
        # valid
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )


# Define a function to check if a WebSocket connection is authenticated
def has_authenticated(websocket: Any) -> bool:
    if len(keys) == 0:
        return True
    param = dict(websocket.query_params)
    if param and param.get("token"):
        x_access_token = param.get("token")
        if x_access_token in keys:
            return True
    return False
