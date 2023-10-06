from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel, root_validator
from pydantic_yaml import YamlModel


class Permutation(BaseModel):
    id: int
    strategy: str
    description: str
    llm: Dict[str, Any] = {}

    @root_validator(pre=True)
    def parse_a_obj(cls, values):
        llm = values.get("llm")
        if llm.get("model") and not llm.get("model_name"):
            llm["model_name"] = llm["model"].lower()
        if llm.get("provider") and llm.get("provider") == "OpenAI":
            llm["provider"] = "OpenAIChat"
        values[
            "description"
        ] = f"{llm.get('provider')}[{llm.get('model_name')}] - [{values.get('strategy')}]"
        return values


class PermutationConfig(BaseModel):
    strategies: List[str] = []
    llms: List[Dict[str, Any]] = []
    permutations: List[Permutation] = []

    @root_validator(pre=True)
    def parse_a_obj(cls, values):
        strategies = values.get("strategies")
        llms = values.get("llms")
        permutations = []
        id = 1
        for strategy in strategies:
            for llm in llms:
                permutations.append(
                    Permutation(
                        id=id,
                        strategy=strategy,
                        llm=llm,
                    )
                )
                id = id + 1
        values["permutations"] = permutations
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


class JobRequest(YamlModel):
    version: str
    name: str
    config: Config
    test_plugin: Plugin
    permutation_config: PermutationConfig
    test_cases: List[TestCase]
    operations: List[str] = []

    def get_total_permutations(self):
        return len(self.permutation_config.permutations)

    def get_job_request_name(self):
        return "{}-{}-{}".format(
            self.name, self.version, datetime.now().strftime("%Y-%m-%d")
        )
