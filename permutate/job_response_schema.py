import csv
import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

from permutate.job_request_schema import Plugin


class JobDetail(BaseModel):
    function_provider: str
    expected_api_used: Optional[str]
    expected_method: Optional[str]
    test_case_id: str
    is_run_completed: bool
    language: str
    prompt: str
    final_output: Optional[str]
    match_score: float
    is_plugin_detected: bool
    is_plugin_operation_found: bool
    is_plugin_parameter_mapped: bool
    plugin_name: Optional[str]
    method: Optional[str]
    plugin_operation: Optional[str]
    plugin_parameters_mapped: Optional[Dict]
    parameter_mapped_percentage: float
    response_time_sec: float
    total_llm_tokens_used: int
    llm_api_cost: Optional[float]

    def get_tool_case_result(self):
        return (
            "Passed"
            if self.is_plugin_detected
            and self.is_plugin_operation_found
            and self.is_plugin_parameter_mapped
            else "Failed"
        )


class JobDetailOut(JobDetail):
    class Config:
        json_encoders = {Decimal: lambda v: float(round(v, 2))}


class JobSummary(BaseModel):
    total_test_cases: int
    failed_cases: int
    language: str
    overall_accuracy: float
    accuracy_step_a: float
    accuracy_step_b: float
    accuracy_step_c: float
    total_run_time: float
    average_response_time_sec: float
    total_llm_tokens_used: int
    average_llm_tokens_used: float
    total_llm_api_cost: Optional[float]

    @staticmethod
    def build_from_details(details: List[JobDetail]):
        total_failed_cases = 0
        total_run_time = 0.0
        total_llm_tokens_used = 0
        total_llm_api_cost = 0.0
        passed_step_a = 0
        passed_step_b = 0
        passed_step_c = 0
        for detail in details:
            if detail.get_tool_case_result() == "Failed":
                total_failed_cases += 1
            total_run_time += (
                detail.response_time_sec if detail.response_time_sec else 0
            )
            total_llm_tokens_used += (
                detail.total_llm_tokens_used if detail.total_llm_tokens_used else 0
            )
            total_llm_api_cost += detail.llm_api_cost if detail.llm_api_cost else 0.0

            passed_step_a += 1 if detail.is_plugin_detected else 0
            passed_step_b += 1 if detail.is_plugin_operation_found else 0
            passed_step_c += 1 if detail.is_plugin_parameter_mapped else 0
        overall_accuracy = 0.0
        if len(details) > 0:
            overall_accuracy = round(
                (len(details) - total_failed_cases) / len(details) * 100, 1
            )
        return JobSummary(
            total_test_cases=len(details),
            failed_cases=total_failed_cases,
            language="English",
            overall_accuracy=overall_accuracy,
            accuracy_step_a=passed_step_a,
            accuracy_step_b=passed_step_b,
            accuracy_step_c=passed_step_c,
            total_run_time=round(total_run_time, 2),
            average_response_time_sec=round(total_run_time / len(details), 2)
            if len(details) > 0
            else 0,
            total_llm_tokens_used=total_llm_tokens_used,
            average_llm_tokens_used=round((total_llm_tokens_used / len(details)), 2)
            if len(details) > 0
            else 0,
            total_llm_api_cost=total_llm_api_cost,
        )


class JobSummaryOut(JobSummary):
    class Config:
        json_encoders = {Decimal: lambda v: float(round(v, 2))}


class JobResponse(BaseModel):
    status: Optional[str] = "job_summary"
    job_name: str
    started_on: datetime
    completed_on: datetime
    test_plugin: Plugin
    summary: JobSummary
    operation_summary: Dict[str, JobSummary]
    permutation_summary: dict[str, JobSummary]
    operation_permutation_summary: dict[str, dict[str, JobSummary]]
    details: List[JobDetail]
    output_directory: Optional[str]

    def group_details(self):
        details = {}
        for detail in self.details:
            if detail.test_case_name not in details:
                details[detail.test_case_name] = []
            details[detail.test_case_name].append(detail)
        return details

    def get_test_cases(self):
        test_cases = {}
        for detail in self.details:
            test_cases[detail.test_case_name] = detail.prompt
        return test_cases

    def get_test_types(self):
        test_cases = {}
        for detail in self.details:
            test_cases[detail.test_case_name] = detail.test_type
        return test_cases

    # TODO need testing after last permutation model refactoring
    def save_to_csv(self, break_down_by_environment: bool = False):
        if not break_down_by_environment:
            fieldnames = list(JobSummary.schema()["properties"].keys())
            summary_filename = f"{self.output_directory}{self.job_name}-summary.csv"
            with open(summary_filename, "w") as fp:
                writer = csv.DictWriter(fp, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(json.loads(JobSummaryOut(**self.summary.dict()).json()))

            fieldnames = list(JobDetail.schema()["properties"].keys())
            detail_filename = f"{self.output_directory}{self.job_name}-details.csv"
            with open(detail_filename, "w") as fp:
                writer = csv.DictWriter(fp, fieldnames=fieldnames)
                writer.writeheader()
                for detail in self.details:
                    writer.writerow(json.loads(JobDetail(**detail.dict()).json()))
            print(f"Summary csv result\n\t{summary_filename}")
            print(f"Details csv result\n\t{detail_filename}")
        else:
            for details in self.details:
                environment_name = details.function_provider
                fieldnames = list(JobSummary.schema()["properties"].keys())
                summary_filename = (
                    f"{self.output_directory}{self.job_name}                   "
                    f" {environment_name}_summary.csv"
                )
                with open(summary_filename, "w") as fp:
                    writer = csv.DictWriter(fp, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerow(
                        json.loads(JobSummaryOut(**self.summary.dict()).json())
                    )

                fieldnames = list(JobDetail.schema()["properties"].keys())
                detail_filename = (
                    f"{self.output_directory}{self.job_name}                   "
                    f" {environment_name}_details.csv"
                )
                with open(detail_filename, "w") as fp:
                    writer = csv.DictWriter(fp, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerow(json.loads(JobDetail(**detail.dict()).json()))
                print(f"Summary csv result\n\t{summary_filename}")
                print(f"Details csv result\n\t{detail_filename}")

    # TODO need testing after last permutation model refactoring
    def build_html_table(self):
        header = [
            "Tool Case Result",
            "Type",
            "Tool",
            "Pipeline",
            "LLM",
            "Model",
            "Language",
            "Response Time(in seconds)",
            "LLM Tokens Used",
            "LLM API Cost",
            "Tool Selected",
        ]
        rows = []
        group_details = self.group_details()
        test_cases = self.get_test_cases()
        test_types = self.get_test_types()
        for test_case_name in group_details:
            r_header = {"data": test_cases.get(test_case_name), "type": "header"}
            rows.append(r_header)
            for detail in group_details.get(test_case_name):
                tool_case_result = detail.get_tool_case_result()
                permutation = self.get_permutation_by_name(detail.function_provider)
                row = [
                    {
                        "data": tool_case_result,
                        "class_name": (
                            "fail" if tool_case_result == "Failed" else "pass"
                        ),
                    },
                    {"data": test_types.get(test_case_name)},
                    {"data": permutation.tool_selector.get("provider")},
                    {"data": permutation.tool_selector.get("pipeline_name")},
                    {"data": permutation.llm.get("provider")},
                    {"data": permutation.llm.get("model_name")},
                    {"data": detail.language},
                    {"data": detail.response_time_sec},
                    {"data": detail.total_llm_tokens_used},
                    {"data": detail.llm_api_cost},
                    {
                        "type": "details",
                        "test_type": test_types.get(test_case_name),
                        "class_name": "details",
                        "plugin": detail.plugin_name,
                        "plugin_found": detail.is_plugin_detected,
                        "operation": detail.plugin_operation,
                        "operation_found": detail.is_plugin_operation_found,
                        "params": detail.plugin_parameters_mapped,
                        "params_found": detail.is_plugin_parameter_mapped,
                    },
                ]
                rows.append({"data": row, "type": "data"})
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_env = Environment(
            loader=FileSystemLoader(searchpath=f"{current_dir}/templates")
        )
        template = template_env.get_template("job_result_template.html")
        summary_headers = [
            "Total Test Cases",
            "Failed Cases",
            "Total Run Time(in sec)",
            "Average Response Time(in sec)",
            "Total Tokens Used",
            "Average Tokens Used",
            "Total API Cost",
        ]
        summary_rows = []
        summary_rows.append(
            [
                {"data": self.summary.total_test_cases},
                {"data": self.summary.failed_cases},
                {"data": self.summary.total_run_time},
                {"data": self.summary.average_response_time_sec},
                {"data": self.summary.total_llm_tokens_used},
                {"data": self.summary.average_llm_tokens_used},
                {"data": self.summary.total_llm_api_cost},
            ]
        )
        plugin = self.test_plugin.manifest_url
        started_on = self.started_on.strftime("%Y-%m-%d %H:%M:%S")
        ended_on = self.completed_on.strftime("%Y-%m-%d %H:%M:%S")
        html = template.render(
            plugin=plugin,
            started_on=started_on,
            ended_on=ended_on,
            summary_headers=summary_headers,
            summary_rows=summary_rows,
            headers=header,
            rows=rows,
        )
        filename = f"{self.job_name}-result.html"

        with open(f"{self.output_directory}{filename}", "w") as f:
            f.write(html)
        print(f"HTML result\n\t{self.output_directory}{filename}")
        absolute_path = os.path.abspath(f"{self.output_directory}{filename}")
        return f"file://{absolute_path}"
