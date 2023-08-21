import json
import asyncio
import threading
from fastapi import APIRouter, WebSocket
from permutate.api.auth import has_authenticated
from permutate import JobRequest, Runner, Plugin, PluginGroup, Permutation, TestCase, \
    Config

router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


def start_batch_job(request_json, websocket):
    job_request = JobRequest(**request_json)
    runner = Runner()
    response = runner.start_request(job_request, output_directory=None,
                                    save_to_html=False, save_to_csv=False, websocket=websocket)
    #websocket.send_text(json.dumps(response))

    try:
        asyncio.run(websocket.close())
    except Exception as e:
        pass


@router.websocket("/ws/start-batch-job")
async def start_batch_job_ws(websocket: WebSocket):
    print(f"CONNECTED TO WEBSOCKET: {websocket}")
    await websocket.accept()
    if has_authenticated(websocket):
        try:
            while True:
                request = await websocket.receive_text()
                request_json = json.loads(request)
                print(f"REQUEST: {request_json}")
                threading.Thread(target=start_batch_job,
                                 args=(request_json, websocket)).start()
        except Exception as e:
            print(e)
    else:
        await websocket.send_text(json.dumps({"error": "Unauthenticated"}))
        await websocket.close()
