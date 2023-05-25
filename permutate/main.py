import json
import requests
import webbrowser
from tqdm import tqdm
from .logger import logger
from datetime import datetime
from prettytable import PrettyTable
from .job_request_schema import JobRequest
from .job_response_schema import JobResponse, JobSummary, JobDetail

pbar = tqdm(total=100)
progress_counter = 25


def permutate(file_path: str, save_to_html=True, save_to_csv=True):
    logger.info("Starting permutate")
    with open(file_path) as f:
        yaml_file = f.read()
    request = JobRequest.parse_raw(yaml_file)

    batch_job_started_on = datetime.now()
    all_details = []
    all_summaries = []
    for permutation in request.permutations:
        permutation_details = single_permutation(request, permutation)
        permutation_summary = JobSummary.build_from_details(permutation_details, permutation.name, 0)
        all_details.extend(permutation_details)
        all_summaries.append(permutation_summary)

    response = JobResponse(
        started_on=batch_job_started_on,
        completed_on=datetime.now(),
        permutations=request.permutations,
        summaries=all_summaries,
        details=all_details
    )
    pbar.close()
    response.save_to_csv(break_down_by_environment=False) if save_to_csv else None
    if save_to_html:
        build_pretty_table(response)
        webbrowser.open("file:///Users/shrikant/Workspace/PythonWorkspace/permutate/workspace/job_result.html")


def build_pretty_table(response: JobResponse):
    table = PrettyTable()
    table = PrettyTable()
    table.format = True
    table.header = False
    table.padding_width = 1
    table.preserve_internal_border = True
    table.border = True
    table.add_row(["Tool", "Pipeline", "LLM", "Model", "Completed?", "Language",
                   "Match Score", "Plugin Detected", "Operation Found", "Parameters Mapped",
                   "Parameter Mapped Percentage", "Response Time(in seconds)", "LLM Tokens Used", "LLM API Cost"])
    for detail in response.details:
        permutation = response.get_permutation_by_name(detail.permutation_name)
        table.add_row([permutation.tool_selector.get("provider"), permutation.tool_selector.get("pipeline_name"),
                       permutation.llm.get("provider"), permutation.llm.get("model_name"), detail.is_run_completed,
                       detail.language, detail.match_score, detail.is_plugin_detected, detail.is_plugin_operation_found,
                       detail.is_plugin_parameter_mapped, detail.parameter_mapped_percentage, detail.response_time_sec,
                       detail.total_llm_tokens_used, detail.llm_api_cost])

    # build and save html
    html_table = table.get_html_string(attributes={"id": "my_table", "class": "red_table"})
    row_index = 1
    css_styling = "background-color: yellow; color: blue;"
    enhanced_row = f'<tr style="{css_styling}">' + html_table.split('\n')[row_index] + "</tr>"
    styled_table_str = '\n'.join([html_table.split('\n')[i] if i != 2 else enhanced_row
                                  for i in range(len(html_table.split('\n')))])
    styled_html_table = f"""
    <style>
        table {{ border-collapse: collapse; margin: 1em 0; }}
        th, td {{ padding: 8px; border: 1px solid black; }}
        thead {{ background-color: lightgray; }}
        /* Add more CSS styles as needed */
    </style>
    {styled_table_str}
    """
    with open("workspace/job_result.html", "w") as f:
        f.write(styled_html_table)


def single_permutation(request, permutation):
    permutation_details = []
    permutation_summary = f"{permutation.llm.get('provider')}[{permutation.llm.get('model_name')}] - {permutation.tool_selector.get('provider')}[{permutation.tool_selector.get('pipeline_name')}]"
    for test_case in request.test_cases:
        pbar.update(progress_counter)
        plugin_group = request.get_plugin_group_from_permutation(permutation)
        detail = run_single_permutation_test_case(
            test_case,
            request.config,
            permutation,
            plugin_group,
            permutation_summary
        )
        permutation_details.append(detail)
        break
    return permutation_details


def run_single_permutation_test_case(test_case, config, permutation, plugin_group, permutation_summary):
    if permutation.tool_selector.get("provider") == "Imprompt":
        url = config.imprompt_tool_selector
    elif permutation.tool_selector.get("provider") == "Langchain":
        url = config.langchain_tool_selector
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
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        response_json = response.json()
        is_plugin_detected = False
        is_plugin_operation_found = False
        is_plugin_parameter_mapped = False
        parameter_mapped_percentage = 0
        for detected_plugin_operation in response_json.get("detected_plugin_operations"):
            if detected_plugin_operation.get("plugin").get("name_for_model") == test_case.expected_plugin_used or \
                    detected_plugin_operation.get("plugin").get("name_for_human") == test_case.expected_plugin_used:
                is_plugin_detected = True
                if detected_plugin_operation.get("plugin").get("api_called") == test_case.expected_api_used:
                    is_plugin_operation_found = True
                extracted_params = detected_plugin_operation.get("mapped_operation_parameters")
                if extracted_params:
                    expected_params = test_case.expected_parameters
                    common_pairs = {k: extracted_params[k] for k in extracted_params if
                                    k in expected_params and extracted_params[k] == expected_params[k]}
                    if len(common_pairs) == len(expected_params):
                        parameter_mapped_percentage = 100
                        is_plugin_parameter_mapped = True
                    else:
                        parameter_mapped_percentage = len(common_pairs) / len(expected_params) * 100
                break
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
            response_time_sec=response_json.get("response_time"),
            total_llm_tokens_used=response_json.get("tokens_used"),
            llm_api_cost=response_json.get("llm_api_cost")
        )
    else:
        detail = JobDetail(
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
    return detail
