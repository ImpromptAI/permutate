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
    openapi_doc_url: str
    server_urls: List[str] = []

    @root_validator(pre=True)
    def parse_a_obj(cls, values):
        openapi_doc_url = values.get("openapi_doc_url")
        openapi_doc_json = requests.get(openapi_doc_url).json()
        if values.get("server_urls") is None:
            values["server_urls"] = []
        for server in openapi_doc_json.get("servers", []):
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
    use_openplugin_library: bool = True
    auto_translate_to_languages: List[str] = []
    tool_selector_endpoint: Optional[str]
    openplugin_api_key: Optional[str]
    openai_api_key: Optional[str]
    mistral_api_key: Optional[str]
    groq_api_key: Optional[str]
    anthropic_api_key: Optional[str]
    cohere_api_key: Optional[str]
    fireworks_api_key: Optional[str]
    together_api_key: Optional[str]
    gemini_api_key: Optional[str]
    aws_access_key_id: Optional[str]
    aws_secret_access_key: Optional[str]
    aws_region_name: Optional[str]
    header: Optional[Dict[str, Any]]


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
