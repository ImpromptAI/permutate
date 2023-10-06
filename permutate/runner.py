import asyncio
import json
import os
import traceback
import webbrowser
from datetime import datetime
from typing import Any, Dict, Optional

import boto3
import requests
from dotenv import load_dotenv
from fastapi import WebSocket
from openplugin.utils.run_plugin_selector import run_api_signature_selector
from tqdm import tqdm

from permutate.job_request_schema import (
    Config,
    JobRequest,
    Permutation,
    Plugin,
    TestCase,
)
from permutate.job_response_schema import JobDetail, JobResponse, JobSummary
from permutate.logger import logger
from permutate.plugin_operation_params import get_plugin_operation_params

# Get the OpenAI API key from the environment variable
load_dotenv()

SINGLE_MODE_ON = False
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")


def send_socket_msg(websocket: Optional[WebSocket], json_msg: dict):
    logger.info(title="socket message", message=json.dumps(json_msg))
    if websocket:
        asyncio.run(websocket.send_text(json.dumps(json_msg)))


# Define a Runner class to handle job execution
class Runner:
    def __init__(self, show_progress_bar: bool = True):
        self.show_progress_bar = show_progress_bar
        if self.show_progress_bar:
            self.pbar = tqdm(total=100)
            self.progress_counter = 0

    def start(
        self,
        file_path: str,
        output_directory: str,
        save_to_html: bool = True,
        save_to_csv: bool = True,
    ) -> None:
        # Load a job request from a YAML file
        with open(file_path) as f:
            yaml_file = f.read()
        request = JobRequest.parse_raw(yaml_file)
        self.start_request(request, output_directory, save_to_html, save_to_csv)

    def start_request(
        self,
        request: JobRequest,
        output_directory: Optional[str],
        save_to_html: bool = True,
        save_to_csv: bool = True,
        websocket: Optional[WebSocket] = None,
        save_to_s3: bool = False,
    ):
        if request.config.openai_api_key is None:
            raise Exception("OpenAI API key is not set")
        logger.info(
            title="batch job started", message=f"{request.get_job_request_name()}"
        )
        # Start a job request and handle its execution
        self.progress_counter = int(
            100 / (request.get_total_permutations() * len(request.test_cases))
        )

        batch_job_started_on = datetime.now()

        send_socket_msg(
            websocket=websocket,
            json_msg={
                "status": "batch_job_started",
                "permutations": [
                    perm.dict() for perm in request.permutation_config.permutations
                ],
                "plugin_operation_params": get_plugin_operation_params(
                    request.test_plugin.manifest_url
                ),
            },
        )

        all_details: list = []

        for operation in request.operations:
            for test_case in request.test_cases:
                operation_key = (
                    f"{test_case.expected_method} {test_case.expected_api_used}"
                )
                if operation_key.lower() != operation.lower():
                    continue
                send_socket_msg(
                    websocket=websocket,
                    json_msg={
                        "status": "test_case_started",
                        "test_case_id": test_case.id,
                    },
                )
                for permutation in request.permutation_config.permutations:
                    send_socket_msg(
                        websocket=websocket,
                        json_msg={
                            "status": "permutation_started",
                            "test_case_id": test_case.id,
                            "permutation_id": permutation.id,
                            "permutation_description": permutation.description,
                            "llm": permutation.llm,
                            "strategy": permutation.strategy,
                        },
                    )
                    detail = self.run_single_permutation_test_case(
                        test_case, request.test_plugin, request.config, permutation
                    )
                    send_socket_msg(
                        websocket=websocket,
                        json_msg={
                            "status": "permutation_ended",
                            "test_case_id": test_case.id,
                            "permutation_id": permutation.id,
                            "permutation_description": permutation.description,
                            "llm": permutation.llm,
                            "strategy": permutation.strategy,
                            "response": detail.dict(),
                        },
                    )
                    all_details.append(detail)
                send_socket_msg(
                    websocket=websocket,
                    json_msg={
                        "status": "test_case_ended",
                        "test_case_id": test_case.id,
                    },
                )
        summary = JobSummary.build_from_details(all_details)

        # build permutation summary
        permutation_summary: dict[int, JobSummary] = {}
        for permutation in request.permutation_config.permutations:
            perm_details = []
            for detail in all_details:
                if detail.permutation_id == permutation.id:
                    perm_details.append(detail)
            permutation_summary[permutation.id] = JobSummary.build_from_details(
                all_details
            )

        response = JobResponse(
            job_name=request.get_job_request_name(),
            started_on=batch_job_started_on,
            completed_on=datetime.now(),
            test_plugin=request.test_plugin,
            summary=summary,
            permutation_summary=permutation_summary,
            details=all_details,
            output_directory=output_directory,
        )
        if websocket is not None:
            asyncio.run(websocket.send_text(response.json()))
        if self.show_progress_bar:
            self.pbar.close()
        response.save_to_csv(break_down_by_environment=False) if save_to_csv else None
        if save_to_html:
            url = response.build_html_table()
            webbrowser.open(url)
        send_socket_msg(
            websocket=websocket,
            json_msg={"status": "batch_job_ended"},
        )

    @staticmethod
    def run_single_permutation_test_case(
        test_case: TestCase,
        test_plugin: Plugin,
        config: Config,
        permutation: Permutation,
    ) -> JobDetail:
        try:
            # Run a single test case for a permutation
            passed = True
            if config.tool_selector_endpoint is None:
                lib_payload = {
                    "messages": [
                        {
                            "content": test_case.prompt,
                            "message_type": "HumanMessage",
                        }
                    ],
                    "plugin": {"manifest_url": test_plugin.manifest_url},
                    "config": config.dict(),
                    "tool_selector_config": {"pipeline_name": permutation.strategy},
                    "llm": permutation.llm,
                }
                response_json = run_api_signature_selector(lib_payload)
            else:
                url = f"{config.tool_selector_endpoint}/api/api-signature-selector"
                payload_str = json.dumps(
                    {
                        "messages": [
                            {
                                "content": test_case.prompt,
                                "message_type": "HumanMessage",
                            }
                        ],
                        "plugin": {"manifest_url": test_plugin.manifest_url},
                        "config": config.dict(),
                        "tool_selector_config": {"pipeline_name": permutation.strategy},
                        "llm": permutation.llm,
                    }
                )

                headers: Dict[Any, Any] = {
                    "x-api-key": config.openplugin_api_key,
                    "Content-Type": "application/json",
                }
                response = requests.request(
                    "POST", url, headers=headers, data=payload_str
                )
                if response.status_code == 401 or response.status_code == 403:
                    raise Exception("Invalid Openplugin API key")
                if response.status_code != 200:
                    passed = False
                response_json = response.json()
            if not passed or response_json is None:
                return JobDetail(
                    permutation_id=permutation.id,
                    permutation_description=permutation.description,
                    test_case_id=test_case.id,
                    is_run_completed=False,
                    language="English",
                    method=None,
                    prompt=test_case.prompt,
                    final_output="FAILED",
                    match_score=0,
                    plugin_name=None,
                    plugin_operation=None,
                    plugin_parameters_mapped=None,
                    is_plugin_detected=False,
                    is_plugin_operation_found=False,
                    is_plugin_parameter_mapped=False,
                    parameter_mapped_percentage=0,
                    response_time_sec=0,
                    total_llm_tokens_used=0,
                    llm_api_cost=0,
                )
            is_plugin_detected = False
            is_plugin_operation_found = False
            is_plugin_parameter_mapped = False
            parameter_mapped_percentage = 0.0
            plugin_operation = None
            plugin_name = None
            plugin_parameters_mapped = None
            method = None
            for detected_plugin_operation in response_json.get(
                "detected_plugin_operations"
            ):
                if (
                    detected_plugin_operation.get("plugin").get("name")
                    == test_case.expected_plugin_used
                    or detected_plugin_operation.get("plugin").get("manifest_url")
                    == test_case.expected_plugin_used
                ):
                    is_plugin_detected = True
                    plugin_name = detected_plugin_operation.get("plugin").get("name")

                    plugin_operation = detected_plugin_operation.get("api_called")
                    if plugin_operation == test_case.expected_api_used:
                        is_plugin_operation_found = True

                    for server_url in test_plugin.server_urls:
                        if (
                            plugin_operation
                            == f"{server_url}{test_case.expected_api_used}"
                        ):
                            is_plugin_operation_found = True
                            plugin_operation = plugin_operation.replace(server_url, "")
                            break
                    method = detected_plugin_operation.get("method")
                    plugin_parameters_mapped = detected_plugin_operation.get(
                        "mapped_operation_parameters"
                    )
                    expected_params = test_case.expected_parameters
                    if expected_params:
                        expected_params = {
                            key: value
                            for key, value in expected_params.items()
                            if value is not None and value != ""
                        }

                    if expected_params:
                        common_pairs = {
                            k: v
                            for k, v in plugin_parameters_mapped.items()
                            if k in expected_params
                            and str(v) == str(expected_params[k])
                        }
                    if (
                        len(common_pairs) == len(expected_params)
                        if expected_params
                        else 0
                    ):
                        parameter_mapped_percentage = 100
                        is_plugin_parameter_mapped = True
                    else:
                        parameter_mapped_percentage = (
                            len(common_pairs)
                            if common_pairs
                            else 0 / len(expected_params)
                            if expected_params
                            else 0
                        ) * 100

            detail = JobDetail(
                permutation_id=permutation.id,
                permutation_description=permutation.description,
                test_case_id=test_case.id,
                is_run_completed=True,
                language="English",
                prompt=test_case.prompt,
                final_output=response_json.get("final_text_response"),
                match_score=0,
                is_plugin_detected=is_plugin_detected,
                is_plugin_operation_found=is_plugin_operation_found,
                is_plugin_parameter_mapped=is_plugin_parameter_mapped,
                parameter_mapped_percentage=parameter_mapped_percentage,
                plugin_name=plugin_name,
                plugin_operation=plugin_operation,
                method=method,
                plugin_parameters_mapped=plugin_parameters_mapped,
                response_time_sec=response_json.get("response_time"),
                total_llm_tokens_used=response_json.get("tokens_used"),
                llm_api_cost=response_json.get("llm_api_cost"),
            )
            return detail
        except Exception as e:
            logger.error(f"Error running permutation: {e} {traceback.format_exc()}")
            return JobDetail(
                permutation_id=permutation.id,
                permutation_description=permutation.description,
                test_case_id=test_case.id,
                is_run_completed=False,
                language="English",
                method=None,
                prompt=test_case.prompt,
                final_output="FAILED",
                match_score=0,
                plugin_name=None,
                plugin_operation=None,
                plugin_parameters_mapped=None,
                is_plugin_detected=False,
                is_plugin_operation_found=False,
                is_plugin_parameter_mapped=False,
                parameter_mapped_percentage=0,
                response_time_sec=0,
                total_llm_tokens_used=0,
                llm_api_cost=0,
            )

    def save_to_s3(self, filename: str, content_type: str, content: str) -> dict:
        # Add to S3 Bucket
        s3 = boto3.client(
            "s3",
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
        )
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=filename,
            Body=content,
            ContentType=content_type,
            ACL="public-read",
        )
        # results = s3.get_object(Bucket=S3_BUCKET_NAME, Key=name)
        full_url = s3.generate_presigned_url(
            "get_object", Params={"Bucket": S3_BUCKET_NAME, "Key": filename}
        )
        return {"s3_url": full_url.split("?")[0]}
