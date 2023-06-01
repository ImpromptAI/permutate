import json
import requests
import webbrowser
from tqdm import tqdm
from .logger import logger
from datetime import datetime
from openplugin import run_plugin_selector
from .job_request_schema import JobRequest
from .job_response_schema import JobResponse, JobSummary, JobDetail


class Runner:

    def __init__(self, show_progress_bar: bool = True):
        self.show_progress_bar = show_progress_bar
        if self.show_progress_bar:
            self.pbar = tqdm(total=100)
            self.progress_counter = None

    def start(self, file_path: str, output_directory: str, save_to_html=True, save_to_csv=True):
        logger.info("Starting permutate")
        with open(file_path) as f:
            yaml_file = f.read()
        request = JobRequest.parse_raw(yaml_file)
        self.progress_counter = 100 / (len(request.permutations) * len(request.test_cases))
        batch_job_started_on = datetime.now()
        all_details = []
        for permutation in request.permutations:
            permutation_details = self.single_permutation(request, permutation)
            all_details.extend(permutation_details)

        summary = JobSummary.build_from_details(all_details)
        response = JobResponse(
            job_name=request.get_job_request_name(),
            started_on=batch_job_started_on,
            completed_on=datetime.now(),
            test_plugin=request.test_plugin,
            permutations=request.permutations,
            summary=summary,
            details=all_details,
            output_directory=output_directory
        )
        if self.show_progress_bar:
            self.pbar.close()
        response.save_to_csv(break_down_by_environment=False) if save_to_csv else None
        if save_to_html:
            url = response.build_html_table()
            webbrowser.open(url)

    def single_permutation(self, request, permutation):
        permutation_details = []
        permutation_summary = f"{permutation.llm.get('provider')}[{permutation.llm.get('model_name')}] - {permutation.tool_selector.get('provider')}[{permutation.tool_selector.get('pipeline_name')}]"
        for test_case in request.test_cases:
            if self.show_progress_bar:
                self.pbar.update(self.progress_counter)
            plugin_group = request.get_plugin_group_from_permutation(permutation)
            detail = self.run_single_permutation_test_case(
                test_case,
                request.config,
                permutation,
                plugin_group,
                permutation_summary
            )
            permutation_details.append(detail)
        return permutation_details

    @staticmethod
    def run_single_permutation_test_case(test_case, config, permutation, plugin_group, permutation_summary):
        payload = json.dumps({
            "messages": [{
                "content": test_case.prompt,
                "message_type": "HumanMessage"
            }],
            "plugins": plugin_group.dict().get("plugins"),
            "config": config.dict(),
            "tool_selector_config": permutation.tool_selector,
            "llm": permutation.llm
        })
        passed = True
        if config.use_openplugin_library:
            try:
                response_json = run_plugin_selector(payload)
                if response_json is None:
                    passed = False
            except Exception as e:
                print(e)
                passed = False
        else:
            if permutation.tool_selector.get("provider") == "Imprompt":
                url = config.imprompt_tool_selector
            elif permutation.tool_selector.get("provider") == "Langchain":
                url = config.langchain_tool_selector
            else:
                raise Exception("Tool selector provider not supported")
            headers = {'Content-Type': 'application/json'}
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code != 200:
                passed = False
            response_json = response.json()

        if not passed or response_json is None:
            return JobDetail(
                permutation_name=permutation.name,
                permutation_summary=permutation_summary,
                test_case_name=test_case.name,
                is_run_completed=False,
                language="English",
                prompt=test_case.prompt,
                final_output=f"FAILED",
                match_score="0.0",
                is_plugin_detected=False,
                is_plugin_operation_found=False,
                is_plugin_parameter_mapped=False,
                parameter_mapped_percentage=0,
                response_time_sec=0,
                total_llm_tokens_used=0,
                llm_api_cost=0
            )

        is_plugin_detected = False
        is_plugin_operation_found = False
        is_plugin_parameter_mapped = False
        parameter_mapped_percentage = 0
        plugin_operation = None
        plugin_name = None
        plugin_parameters_mapped = None
        for detected_plugin_operation in response_json.get("detected_plugin_operations"):
            if detected_plugin_operation.get("plugin").get("name_for_model") == test_case.expected_plugin_used or \
                    detected_plugin_operation.get("plugin").get("name_for_human") == test_case.expected_plugin_used:
                is_plugin_detected = True
                plugin_name = detected_plugin_operation.get("plugin").get("name_for_human")
                if detected_plugin_operation.get("plugin").get("api_called") == test_case.expected_api_used:
                    is_plugin_operation_found = True
                plugin_operation = detected_plugin_operation.get("plugin").get("api_called")
                plugin_parameters_mapped = detected_plugin_operation.get("mapped_operation_parameters")
                if plugin_parameters_mapped:
                    expected_params = test_case.expected_parameters
                    common_pairs = {k: plugin_parameters_mapped[k] for k in plugin_parameters_mapped if
                                    k in expected_params and plugin_parameters_mapped[k] == expected_params[k]}
                    if len(common_pairs) == len(expected_params):
                        parameter_mapped_percentage = 100
                        is_plugin_parameter_mapped = True
                    else:
                        parameter_mapped_percentage = len(common_pairs) / len(expected_params) * 100

        detail = JobDetail(
            permutation_name=permutation.name,
            permutation_summary=permutation_summary,
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
            llm_api_cost=response_json.get("llm_api_cost")
        )
        return detail
