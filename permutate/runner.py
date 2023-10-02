import asyncio
import json
import os
import traceback
import webbrowser
from datetime import datetime
from typing import Optional

import boto3
import requests
from dotenv import load_dotenv
from fastapi import WebSocket
from openplugin.utils.run_plugin_selector import (
    run_api_signature_selector,
    run_plugin_selector,
)
from tqdm import tqdm

from permutate.job_request_schema import (
    Config,
    JobRequest,
    Permutation,
    Plugin,
    PluginGroup,
    TestCase,
)
from permutate.job_response_schema import JobDetail, JobResponse, JobSummary
from permutate.logger import logger

# Get the OpenAI API key from the environment variable
load_dotenv()

SINGLE_MODE_ON = False
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
        all_details = []
        for permutation in (
            request.plugin_selector_permutations
            + request.operation_selector_permutations
        ):
            permutation_details = []
            for llm in permutation.get_llms():
                permutation_summary = (
                    f"{llm.get('provider')}[{llm.get('model_name')}] -"
                    f" [{permutation.tool_selector.pipeline_name}]"
                )
                for test_case in request.test_cases:
                    if self.show_progress_bar:
                        self.pbar.update(self.progress_counter)
                    for p_group in request.plugin_groups:
                        logger.info(
                            title="permutation run started",
                            message=(
                                f"Running permutation for: "
                                f"{permutation.permutation_type}, "
                                f" {permutation_summary},plugin_group="
                                f" {p_group.name},test_case= {test_case.name}"
                            ),
                        )
                        detail = self.run_single_permutation_test_case(
                            test_case,
                            request.test_plugin,
                            request.config,
                            permutation,
                            p_group,
                            permutation_summary,
                            llm,
                        )
                        logger.info(
                            title="permutation run ended",
                            message=f"is_run_completed={detail.is_run_completed}",
                        )
                        if SINGLE_MODE_ON:
                            break
                    if websocket is not None:
                        asyncio.run(websocket.send_text(detail.json()))
                    permutation_details.append(detail)
                    if SINGLE_MODE_ON:
                        break
                if SINGLE_MODE_ON:
                    break
            all_details.extend(permutation_details)
            if SINGLE_MODE_ON:
                break
        summary = JobSummary.build_from_details(all_details)
        response = JobResponse(
            job_name=request.get_job_request_name(),
            started_on=batch_job_started_on,
            completed_on=datetime.now(),
            test_plugin=request.test_plugin,
            plugin_selector_permutations=request.plugin_selector_permutations,
            operation_selector_permutations=request.operation_selector_permutations,
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

        return response

    @staticmethod
    def run_single_permutation_test_case(
        test_case: TestCase,
        test_plugin: Plugin,
        config: Config,
        permutation: Permutation,
        plugin_group: PluginGroup,
        permutation_summary: str,
        llm: dict,
    ) -> JobDetail:
        try:
            # Run a single test case for a permutation
            passed = True
            all_plugins = plugin_group.dict().get("plugins")
            all_plugins.append(test_plugin.dict())
            # Determine the type of test case
            # (Plugin Selector or API Signature Selector)
            if config.tool_selector_endpoint is None:
                if permutation.get_permutation_type() == "plugin_selector":
                    payload = {
                        "messages": [
                            {
                                "content": test_case.prompt,
                                "message_type": "HumanMessage",
                            }
                        ],
                        "plugins": all_plugins,
                        "config": config.dict(),
                        "tool_selector_config": {
                            "pipeline_name": permutation.tool_selector.pipeline_name
                        },
                        "llm": llm,
                    }
                    response_json = run_plugin_selector(payload)
                elif permutation.get_permutation_type() == "operation_selector":
                    payload = {
                        "messages": [
                            {
                                "content": test_case.prompt,
                                "message_type": "HumanMessage",
                            }
                        ],
                        "plugin": {"manifest_url": test_plugin.manifest_url},
                        "config": config.dict(),
                        "tool_selector_config": {
                            "pipeline_name": permutation.tool_selector.pipeline_name
                        },
                        "llm": llm,
                    }
                    response_json = run_api_signature_selector(payload)
                else:
                    raise Exception("Incorrect test case type")
            else:
                if permutation.get_permutation_type() == "plugin_selector":
                    url = f"{config.tool_selector_endpoint}/api/plugin-selector"
                    # TODO: change this
                    payload = json.dumps(
                        {
                            "messages": [
                                {
                                    "content": test_case.prompt,
                                    "message_type": "HumanMessage",
                                }
                            ],
                            "plugins": all_plugins,
                            "config": config.dict(),
                            "tool_selector_config": {
                                "pipeline_name": permutation.tool_selector.pipeline_name
                            },
                            "llm": llm,
                        }
                    )
                elif permutation.get_permutation_type() == "operation_selector":
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
                            "tool_selector_config": {
                                "pipeline_name": permutation.tool_selector.pipeline_name
                            },
                            "llm": llm,
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
                    test_type=permutation.get_permutation_type(),
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
                        permutation.get_permutation_type() == "operation_selector"
                        and plugin_parameters_mapped
                    ):
                        expected_params = test_case.expected_parameters
                        common_pairs = {
                            k: plugin_parameters_mapped[k]
                            for k in plugin_parameters_mapped
                            if k in expected_params
                            and str(plugin_parameters_mapped[k])
                            == str(expected_params[k])
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
                test_type=permutation.get_permutation_type(),
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
        except Exception as e:
            logger.error(f"Error running permutation: {e} {traceback.format_exc()}")
            return JobDetail(
                permutation_name=permutation.name,
                permutation_summary=permutation_summary,
                test_type=permutation.get_permutation_type(),
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
