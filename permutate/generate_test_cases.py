from pydantic import BaseModel
from typing import List, Optional
import requests
import json


class Path(BaseModel):
    path: str
    method: str


class GenerateTestCase(BaseModel):
    openplugin_manifest_url: str
    openai_api_key: str
    for_paths: Optional[List[Path]] = []

    def generate_test_cases(self):
        openplugin_manifest_json = requests.get(self.openplugin_manifest_url).json()
        plugin_operations = openplugin_manifest_json.get("plugin_operations", {})
        for path in plugin_operations.keys():
            for method in plugin_operations.get(path):
                if self.for_paths and len(self.for_paths) > 0:
                    if not any([path == p.path and method == p.method for p in
                                self.for_paths]):
                        continue
                human_usage_examples = plugin_operations.get(path).get(method).get(
                    "human_usage_examples", [])
                more_examples = []
                for example in human_usage_examples:
                    more_examples.extend(self.generate_variations(example))
                human_usage_examples.extend(more_examples)
        return openplugin_manifest_json

    def generate_variations(self, human_usage_example):
        url = "https://api.openai.com/v1/chat/completions"
        payload = json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant who generates human usage examples."
                },
                {
                    "role": "user",
                    "content": f"Generate 5 sample variations of this usage example: {human_usage_example}"
                }
            ]
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.openai_api_key}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        choices = response.json().get("choices", [])[0].get("message", {}).get(
            "content")
        res = []
        for choice in choices.splitlines():
            if len(choice) >= 2 and choice[0].isdigit() and choice[1] == '.':
                res.append(choice[2:].strip())
            else:
                res.append(choice)
        return res


'''
obj = GenerateTestCase(
    openai_api_key="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",
    openplugin_manifest_url="https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json",
    paths=["/users", "/groups"]
)
print(obj.generate_test_cases())
'''
# ex = "Email the report to shrikant@brandops.io"
# obj.generate_variations(ex)
