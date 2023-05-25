from pydantic import BaseModel
from pydantic_yaml import YamlModel
from typing import List, Optional, Dict


class Permutation(BaseModel):
    name: str
    llm: Dict
    tool_selector: Dict


class Plugin(BaseModel):
    manifest_url: str


class PluginGroup(BaseModel):
    name: str
    plugins: Dict
    plugins: List[Plugin]


class TestCase(BaseModel):
    name: str
    prompt: str
    expected_plugin_used: str
    expected_api_used: str
    expected_parameters: Dict[str, str]
    expected_response: str


class Config(BaseModel):
    openai_api_key: Optional[str]
    langchain_tool_selector: Optional[str]
    imprompt_tool_selector: Optional[str]
    auto_translate_to_languages: List[str]


class JobRequest(YamlModel):
    version: str
    config: Config
    plugin_groups: List[PluginGroup]
    permutations: List[Permutation]
    test_cases: List[TestCase]

    def get_plugin_group_from_name(self, plugin_group_name: str) -> PluginGroup:
        for plugin_group in self.plugin_groups:
            if plugin_group.name == plugin_group_name:
                return plugin_group

    def get_plugin_group_from_permutation(self, permutation: Permutation) -> PluginGroup:
        for plugin_group in self.plugin_groups:
            if plugin_group.name == permutation.tool_selector.get("plugin_group_name"):
                return plugin_group
