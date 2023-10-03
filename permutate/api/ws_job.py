import asyncio
import json
import threading
from typing import Any

from fastapi import APIRouter, WebSocket

from permutate import JobRequest, Runner
from permutate.api.auth import has_authenticated

# Create a FastAPI router
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


def close(websocket: WebSocket):
    try:
        # Try to close the WebSocket connection
        asyncio.run(websocket.close())
    except Exception as e:
        print(e)
        pass


# Define a function to start a batch job
def start_batch_job(request_json: dict, websocket: WebSocket) -> Any:
    # Create a JobRequest object from the provided JSON data
    job_request = JobRequest(**request_json)
    if len(job_request.test_cases) == 0:
        asyncio.run(
            websocket.send_text(json.dumps({"error": "No test cases provided"}))
        )
        close(websocket)
        raise Exception("No test cases provided")
    runner = Runner(show_progress_bar=False)
    # Start the batch job and get the response
    runner.start_request(
        job_request,
        output_directory=None,
        save_to_html=False,
        save_to_csv=False,
        websocket=websocket,
    )
    close(websocket)


# Define a WebSocket route for starting batch jobs
@router.websocket("/ws/start-interactive-job")
async def start_batch_job_ws(websocket: WebSocket):
    # logger.info(f"CONNECTED TO WEBSOCKET: {websocket}")
    # Accept the WebSocket connection
    await websocket.accept()
    # Check if the WebSocket is authenticated
    if has_authenticated(websocket):
        try:
            while True:
                # Receive and parse JSON data from the WebSocket
                request = await websocket.receive_text()
                request_json = json.loads(request)
                # Start the batch job in a separate thread
                threading.Thread(
                    target=start_batch_job, args=(request_json, websocket)
                ).start()
        except Exception as e:
            print(e)
    else:
        # Send an error message and close the WebSocket if unauthenticated
        await websocket.send_text(json.dumps({"error": "Unauthenticated"}))
        await websocket.close()
