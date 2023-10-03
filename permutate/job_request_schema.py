from abc import abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, root_validator
from pydantic_yaml import YamlModel


class ToolSelector(BaseModel):
    pipeline_name: str
    llms: List[Dict[str, Any]] = []

    @root_validator(pre=True)
    def parse_a_obj(cls, values):
        llms = values.get("llms", [])
        for llm in llms:
            if llm.get("model") and not llm.get("model_name"):
                llm["model_name"] = llm["model"].lower()
            if llm.get("provider") and llm.get("provider") == "OpenAI":
                llm["provider"] = "OpenAIChat"
        return values


class Permutation(BaseModel):
    name: str
    tool_selector: ToolSelector

    @abstractmethod
    def get_permutation_type(self):
        pass

    def get_llms(self):
        return self.tool_selector.llms

    def get_llm_provider(self):
        return self.tool_selector.pipeline_name.split("_")[0]


class PluginSelectorPermutation(Permutation):
    permutation_type: str = "plugin_selector"

    def get_permutation_type(self) -> str:
        return self.permutation_type


class OperationSelectorPermutation(Permutation):
    permutation_type: str = "operation_selector"

    def get_permutation_type(self) -> str:
        return self.permutation_type


class Plugin(BaseModel):
    manifest_url: str


class PluginGroup(BaseModel):
    name: str
    plugins: List[Plugin]


class TestCase(BaseModel):
    id: str
    name: Optional[str]
    prompt: str
    expected_response: Optional[str]
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
    plugin_groups: List[PluginGroup]
    plugin_selector_permutations: List[PluginSelectorPermutation]
    operation_selector_permutations: List[OperationSelectorPermutation]
    test_cases: List[TestCase]
    operations: List[str] = []

    def get_total_permutations(self):
        return len(self.plugin_selector_permutations) + len(
            self.operation_selector_permutations
        )

    def get_plugin_group_from_name(
        self, plugin_group_name: str
    ) -> Optional[PluginGroup]:
        for plugin_group in self.plugin_groups:
            if plugin_group.name == plugin_group_name:
                return plugin_group
        return None

    def get_job_request_name(self):
        return "{}-{}-{}".format(
            self.name, self.version, datetime.now().strftime("%Y-%m-%d")
        )
