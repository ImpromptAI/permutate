import requests
from datetime import datetime
from pydantic_yaml import YamlModel
from typing import List, Optional, Dict
from pydantic import BaseModel, root_validator


class Permutation(BaseModel):
    name: str
    llm: Dict
    tool_selector: Dict


class Plugin(BaseModel):
    schema_version: Optional[str]
    name_for_model: Optional[str]
    name_for_human: Optional[str]
    description_for_model: Optional[str]
    description_for_human: Optional[str]
    logo_url: Optional[str]
    contact_email: Optional[str]
    legal_info_url: Optional[str]
    manifest_url: str

    @root_validator(pre=True)
    def _set_fields(cls, values: dict) -> dict:
        """This is a validator that sets the field values based on the manifest_url"""
        if values.get("manifest_url"):
            manifest_obj = requests.get(values.get("manifest_url")).json()
            for key in manifest_obj.keys():
                if key not in values.keys():
                    values[key] = manifest_obj[key]
        return values


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
    name: str
    config: Config
    test_plugin: Plugin
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

    def get_job_request_name(self):
        return "{}-{}-{}".format(self.name, self.version, datetime.now().strftime("%Y-%m-%d"))
