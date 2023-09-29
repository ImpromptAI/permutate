from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel
from pydantic_yaml import YamlModel


class Permutation(BaseModel):
    name: str
    llm: Dict
    tool_selector: Dict


class Plugin(BaseModel):
    manifest_url: str


class PluginGroup(BaseModel):
    name: str
    plugins: List[Plugin]


class TestCaseType(Enum):
    PLUGIN_SELECTOR = "plugin_selector"
    API_SIGNATURE_SELECTOR = "api_signature_selector"


class TestCase(BaseModel):
    name: str
    prompt: str
    type: TestCaseType
    expected_response: Optional[str]
    expected_plugin_used: Optional[str]
    expected_api_used: Optional[str]
    expected_method: Optional[str]
    expected_parameters: Optional[Dict[str, str]]


class Config(BaseModel):
    openplugin_api_key: Optional[str]
    use_openplugin_library: bool = True
    openai_api_key: Optional[str]
    tool_selector_endpoint: Optional[str]


class JobRequest(YamlModel):
    version: str
    name: str
    config: Config
    test_plugin: Plugin
    plugin_groups: List[PluginGroup]
    permutations: List[Permutation]
    test_cases: List[TestCase]

    def get_plugin_group_from_name(
        self, plugin_group_name: str
    ) -> Optional[PluginGroup]:
        for plugin_group in self.plugin_groups:
            if plugin_group.name == plugin_group_name:
                return plugin_group
        return None

    def get_plugin_group_from_permutation(
        self, permutation: Permutation
    ) -> Optional[PluginGroup]:
        for plugin_group in self.plugin_groups:
            if plugin_group.name == permutation.tool_selector.get("plugin_group_name"):
                return plugin_group
        return None

    def get_job_request_name(self):
        return "{}-{}-{}".format(
            self.name, self.version, datetime.now().strftime("%Y-%m-%d")
        )
