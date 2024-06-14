from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel, root_validator
from pydantic_yaml import YamlModel


class FunctionProvider(BaseModel):
    name: str


class PermutationConfig(BaseModel):
    function_providers: List[FunctionProvider]

    @root_validator(pre=True)
    def parse_a_obj(cls, values):
        return values


class Plugin(BaseModel):
    manifest_url: str
    server_urls: List[str] = []

    @root_validator(pre=True)
    def parse_a_obj(cls, values):
        openplugin_manifest_url = values.get("manifest_url")
        openplugin_manifest_json = requests.get(openplugin_manifest_url).json()
        openapi_json = requests.get(
            openplugin_manifest_json["openapi_doc_url"]
        ).json()
        if values.get("server_urls") is None:
            values["server_urls"] = []
        for server in openapi_json.get("servers", []):
            values["server_urls"].append(server["url"])
        return values


class TestCase(BaseModel):
    id: str
    prompt: str
    expected_plugin_used: Optional[str]
    expected_api_used: Optional[str]
    expected_method: Optional[str]
    expected_parameters: Optional[Dict[str, Any]]


class Config(BaseModel):
    openplugin_api_key: Optional[str]
    use_openplugin_library: bool = True
    openai_api_key: Optional[str]
    auto_translate_to_languages: List[str] = []
    tool_selector_endpoint: Optional[str]
    cohere_api_key: Optional[str]
    google_palm_key: Optional[str]
    aws_access_key_id: Optional[str]
    aws_secret_access_key: Optional[str]
    aws_region_name: Optional[str]


class JobRequest(YamlModel):
    version: str
    name: str
    config: Config
    test_plugin: Plugin
    permutation_config: PermutationConfig
    test_cases: List[TestCase]
    operations: List[str] = []

    def get_total_permutations(self):
        return len(self.permutation_config.function_providers)

    def get_job_request_name(self):
        return "{}-{}-{}".format(
            self.name, self.version, datetime.now().strftime("%Y-%m-%d")
        )
