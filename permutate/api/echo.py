import json
from typing import Any

from fastapi import APIRouter, Depends, WebSocket
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from permutate.api import auth

# Create a FastAPI router
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


# Define a route to get LLM permutations
@router.get("/echo")
def echo_message(
    api_key: APIKey = Depends(auth.get_api_key),
) -> Any:
    print("GET ECHO")
    return JSONResponse(status_code=200, content={"message": "echo"})


# Define a WebSocket route for starting batch jobs
@router.websocket("/ws/echo")
async def start_batch_job_ws(websocket: WebSocket):
    # logger.info(f"CONNECTED TO WEBSOCKET: {websocket}")
    # Accept the WebSocket connection
    print("11")
    await websocket.accept()
    print("WS ECHO")
    # Check if the WebSocket is authenticated
    try:
        while True:
            # Receive and parse JSON data from the WebSocket
            request = await websocket.receive_text()
            request_json = json.loads(request)
            print(request_json)
    except Exception as e:
        print(e)
