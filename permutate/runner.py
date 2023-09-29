import asyncio
import json
import os
import webbrowser
from datetime import datetime
from typing import Any, Optional

import boto3
import requests
from dotenv import load_dotenv
from fastapi import WebSocket
from openplugin import run_api_signature_selector, run_plugin_selector
from tqdm import tqdm

from .job_request_schema import JobRequest, TestCaseType
from .job_response_schema import JobDetail, JobResponse, JobSummary
from .logger import logger

# Get the OpenAI API key from the environment variable
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")


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
        logger.info("Starting permutate")
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
    ) -> JobResponse:
        # Start a job request and handle its execution
        self.progress_counter = int(
            100 / (len(request.permutations) * len(request.test_cases))
        )

        batch_job_started_on = datetime.now()
        all_details = []
        for permutation in request.permutations:
            permutation_details = self.single_permutation(
                request, permutation, websocket
            )
            all_details.extend(permutation_details)
            break

        summary = JobSummary.build_from_details(all_details)
        response = JobResponse(
            job_name=request.get_job_request_name(),
            started_on=batch_job_started_on,
            completed_on=datetime.now(),
            test_plugin=request.test_plugin,
            permutations=request.permutations,
            summary=summary,
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
        if save_to_s3:
            print("---")
        return response

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
        public_url = full_url.split("?")[0]
        return {"s3_url": public_url}

    def single_permutation(
        self, request: Any, permutation: Any, websocket: Optional[WebSocket] = None
    ) -> Any:
        # Execute a single permutation of a job request
        permutation_details = []
        permutation_summary = f"{permutation.llm.get('provider')}[{permutation.llm.get('model_name')}] - {permutation.tool_selector.get('provider')}[{permutation.tool_selector.get('pipeline_name')}]"
        for test_case in request.test_cases:
            if self.show_progress_bar:
                self.pbar.update(self.progress_counter)
            plugin_group = request.get_plugin_group_from_permutation(permutation)
            detail = self.run_single_permutation_test_case(
                test_case,
                request.test_plugin,
                request.config,
                permutation,
                plugin_group,
                permutation_summary,
            )
            if websocket is not None:
                asyncio.run(websocket.send_text(detail.json()))
            permutation_details.append(detail)
            break
        return permutation_details

    @staticmethod
    def run_single_permutation_test_case(
        test_case: Any,
        test_plugin: Any,
        config: Any,
        permutation: Any,
        plugin_group: Any,
        permutation_summary: Any,
    ) -> Any:
        # Run a single test case for a permutation
        passed = True
        # Determine the type of test case (Plugin Selector or API Signature Selector)
        if config.tool_selector_endpoint is None:
            if test_case.type == TestCaseType.PLUGIN_SELECTOR:
                payload = {
                    "messages": [
                        {"content": test_case.prompt, "message_type": "HumanMessage"}
                    ],
                    "plugins": plugin_group.dict().get("plugins"),
                    "config": config.dict(),
                    "tool_selector_config": permutation.tool_selector,
                    "llm": permutation.llm,
                }
                if config.openai_api_key is None:
                    if OPENAI_API_KEY is None:
                        raise Exception("OpenAI API key is not set")
                    payload["config"]["openai_api_key"] = OPENAI_API_KEY

                response_json = run_plugin_selector(payload)
            elif test_case.type == TestCaseType.API_SIGNATURE_SELECTOR:
                payload = {
                    "messages": [
                        {"content": test_case.prompt, "message_type": "HumanMessage"}
                    ],
                    "plugin": {"manifest_url": test_plugin.manifest_url},
                    "config": config.dict(),
                    "tool_selector_config": permutation.tool_selector,
                    "llm": permutation.llm,
                }
                if config.openai_api_key is None:
                    if OPENAI_API_KEY is None:
                        raise Exception("OpenAI API key is not set")
                    payload["config"]["openai_api_key"] = OPENAI_API_KEY
                response_json = run_api_signature_selector(payload)
            else:
                raise Exception("Incorrect test case type")
        else:
            if test_case.type == TestCaseType.PLUGIN_SELECTOR:
                url = f"{config.tool_selector_endpoint}/api/plugin-selector"
                payload = json.dumps(
                    {
                        "messages": [
                            {
                                "content": test_case.prompt,
                                "message_type": "HumanMessage",
                            }
                        ],
                        "plugins": plugin_group.dict().get("plugins"),
                        "config": config.dict(),
                        "tool_selector_config": permutation.tool_selector,
                        "llm": permutation.llm,
                    }
                )
            elif test_case.type == TestCaseType.API_SIGNATURE_SELECTOR:
                url = f"{config.tool_selector_endpoint}/api/api-signature-selector"
                payload = json.dumps(
                    {
                        "messages": [
                            {
                                "content": test_case.prompt,
                                "message_type": "HumanMessage",
                            }
                        ],
                        "plugin": {"manifest_url": test_plugin.manifest_url},
                        "config": config.dict(),
                        "tool_selector_config": permutation.tool_selector,
                        "llm": permutation.llm,
                    }
                )
            else:
                raise Exception("Incorrect test case type")
            headers = {
                "x-api-key": config.openplugin_api_key,
                "Content-Type": "application/json",
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 401 or response.status_code == 403:
                raise Exception("Invalid Openplugin API key")
            if response.status_code != 200:
                passed = False
            response_json = response.json()
        if not passed or response_json is None:
            return JobDetail(
                permutation_name=permutation.name,
                permutation_summary=permutation_summary,
                test_type=test_case.type.value,
                test_case_name=test_case.name,
                is_run_completed=False,
                language="English",
                prompt=test_case.prompt,
                final_output="FAILED",
                match_score="0.0",
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
        parameter_mapped_percentage = 0
        plugin_operation = None
        plugin_name = None
        plugin_parameters_mapped = None
        for detected_plugin_operation in response_json.get(
            "detected_plugin_operations"
        ):
            if (
                detected_plugin_operation.get("plugin").get("manifest_url")
                == test_case.expected_plugin_used
            ):
                is_plugin_detected = True
                plugin_name = detected_plugin_operation.get("plugin").get("name")
                if (
                    detected_plugin_operation.get("api_called")
                    == test_case.expected_api_used
                ):
                    is_plugin_operation_found = True
                plugin_operation = detected_plugin_operation.get("api_called")
                plugin_parameters_mapped = detected_plugin_operation.get(
                    "mapped_operation_parameters"
                )

                if (
                    test_case.type == TestCaseType.API_SIGNATURE_SELECTOR
                    and plugin_parameters_mapped
                ):
                    expected_params = test_case.expected_parameters
                    common_pairs = {
                        k: plugin_parameters_mapped[k]
                        for k in plugin_parameters_mapped
                        if k in expected_params
                        and str(plugin_parameters_mapped[k]) == str(expected_params[k])
                    }
                    if len(common_pairs) == len(expected_params):
                        parameter_mapped_percentage = 100
                        is_plugin_parameter_mapped = True
                    else:
                        parameter_mapped_percentage = (
                            len(common_pairs) / len(expected_params) * 100
                        )

        detail = JobDetail(
            permutation_name=permutation.name,
            permutation_summary=permutation_summary,
            test_type=test_case.type.value,
            test_case_name=test_case.name,
            is_run_completed=True,
            language="English",
            prompt=test_case.prompt,
            final_output=response_json.get("final_text_response"),
            match_score="0.0",
            is_plugin_detected=is_plugin_detected,
            is_plugin_operation_found=is_plugin_operation_found,
            is_plugin_parameter_mapped=is_plugin_parameter_mapped,
            parameter_mapped_percentage=parameter_mapped_percentage,
            plugin_name=plugin_name,
            plugin_operation=plugin_operation,
            plugin_parameters_mapped=plugin_parameters_mapped,
            response_time_sec=response_json.get("response_time"),
            total_llm_tokens_used=response_json.get("tokens_used"),
            llm_api_cost=response_json.get("llm_api_cost"),
        )
        return detail
