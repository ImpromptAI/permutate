import asyncio
import json
import threading
from typing import Any

from fastapi import APIRouter, WebSocket
from openplugin.utils.run_plugin_selector import run_api_signature_selector

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


def send_socket_message(json_msg: dict, websocket: WebSocket):
    asyncio.run(websocket.send_text(json.dumps(json_msg)))


# Define a function to start a batch job
def start_test_case(request_json: dict, wsocket: WebSocket) -> Any:
    # Create a JobRequest object from the provided JSON data
    openplugin_manifest_url = request_json.get("openplugin_manifest_url")
    if openplugin_manifest_url is None:
        send_socket_message(
            {
                "error": True,
                "message": "You must supply openplugin_manifest_url",
            },
            wsocket,
        )
        raise Exception("openplugin_manifest_url is required")
    test_case = request_json.get("test_case")
    if test_case is None:
        send_socket_message(
            {"error": True, "message": "You must supply test_case"},
            wsocket,
        )
        raise Exception("test_case is required")
    openai_api_key = request_json.get("openai_api_key")
    if openai_api_key is None:
        send_socket_message(
            {"error": True, "message": "You must supply openai_api_key"},
            wsocket,
        )
        raise Exception("openai_api_key is required")
    try:
        payload = json.dumps(
            {
                "messages": [{"content": test_case, "message_type": "HumanMessage"}],
                "plugin": {"manifest_url": openplugin_manifest_url},
                "config": {
                    "use_openplugin_library": True,
                    "openai_api_key": openai_api_key,
                    "auto_translate_to_languages": [],
                },
                "tool_selector_config": {"pipeline_name": "OAI Functions"},
                "llm": {
                    "provider": "OpenAIChat",
                    "model": "gpt-4",
                    "temperature": 0.4,
                    "max_tokens": 2048,
                    "top_p": 1,
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                    "model_name": "gpt-4",
                },
            }
        )
        response_json = run_api_signature_selector(payload)
        if (
            response_json
            and len(response_json.get("detected_plugin_operations")) > 0
        ):
            send_socket_message(
                {
                    "parameters": response_json.get("detected_plugin_operations")[
                        0
                    ].get("mapped_operation_parameters")
                },
                wsocket,
            )
        else:
            send_socket_message(
                {},
                wsocket,
            )
    except Exception as e:
        print(e)
        import traceback

        traceback.print_exc()
    close(wsocket)


# Define a WebSocket route for starting batch jobs
@router.websocket("/ws/run-test-case")
async def run_test_case(websocket: WebSocket):
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
                    target=start_test_case, args=(request_json, websocket)
                ).start()
        except Exception as e:
            print(e)
    else:
        # Send an error message and close the WebSocket if unauthenticated
        await websocket.send_text(json.dumps({"error": "Unauthenticated"}))
        await websocket.close()
