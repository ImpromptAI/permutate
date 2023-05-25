import csv, json
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from .job_request_schema import Permutation


class JobDetail(BaseModel):
    permutation_name: str
    permutation_summary: str
    test_case_name: str
    is_run_completed: bool
    language: str
    prompt: str
    final_output: Optional[str]
    match_score: float
    is_plugin_detected: bool
    is_plugin_operation_found: bool
    is_plugin_parameter_mapped: bool
    parameter_mapped_percentage: float
    response_time_sec: float
    total_llm_tokens_used: int
    llm_api_cost: Optional[float]


class JobDetailOut(JobDetail):
    class Config:
        json_encoders = {Decimal: lambda v: float(round(v, 2))}


class JobSummary(BaseModel):
    permutation_name: str
    permutation_summary: str
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
    average_llm_tokens_used: int
    total_llm_api_cost: Optional[float]

    @staticmethod
    def build_from_details(details: List[JobDetail], permuation_name: str, total_run_time: float):
        summary = JobSummary(
            permutation_name=permuation_name,
            permutation_summary=details[0].permutation_summary,
            total_test_cases=len(details),
            failed_cases=0,
            language="English",
            overall_accuracy=0,
            accuracy_step_a=0.0,
            accuracy_step_b=0.0,
            accuracy_step_c=0.0,
            total_run_time=total_run_time,
            average_response_time_sec=0.0,
            total_llm_tokens_used=0,
            average_llm_tokens_used=2,
            total_llm_api_cost=0
        )
        return summary


class JobSummaryOut(JobSummary):
    class Config:
        json_encoders = {Decimal: lambda v: float(round(v, 2))}


class JobResponse(BaseModel):
    started_on: datetime
    completed_on: datetime
    permutations: List[Permutation]
    summaries: List[JobSummary]
    details: List[JobDetail]

    def get_permutation_by_name(self, name: str):
        for permutation in self.permutations:
            if permutation.name == name:
                return permutation

    def save_to_csv(self, break_down_by_environment: bool = False):
        file_location = "workspace/"
        if not break_down_by_environment:
            fieldnames = list(JobSummary.schema()["properties"].keys())
            with open(f"{file_location}summary.csv", "w") as fp:
                writer = csv.DictWriter(fp, fieldnames=fieldnames)
                writer.writeheader()
                for summary in self.summaries:
                    writer.writerow(json.loads(JobSummaryOut(**summary.dict()).json()))

            fieldnames = list(JobDetail.schema()["properties"].keys())
            with open(f"{file_location}details.csv", "w") as fp:
                writer = csv.DictWriter(fp, fieldnames=fieldnames)
                writer.writeheader()
                for detail in self.details:
                    writer.writerow(json.loads(JobDetail(**detail.dict()).json()))
        else:
            for permutation in self.permutations:
                environment_name = permutation.name
                fieldnames = list(JobSummary.schema()["properties"].keys())
                with open(f"{file_location}{environment_name}_summary.csv", "w") as fp:
                    writer = csv.DictWriter(fp, fieldnames=fieldnames)
                    writer.writeheader()
                    for summary in self.summaries:
                        if summary.permutation_name == permutation.name:
                            writer.writerow(json.loads(JobSummaryOut(**summary.dict()).json()))

                fieldnames = list(JobDetail.schema()["properties"].keys())
                with open(f"{file_location}{environment_name}_details.csv", "w") as fp:
                    writer = csv.DictWriter(fp, fieldnames=fieldnames)
                    writer.writeheader()
                    for detail in self.details:
                        if detail.permutation_name == permutation.name:
                            writer.writerow(json.loads(JobDetail(**detail.dict()).json()))
