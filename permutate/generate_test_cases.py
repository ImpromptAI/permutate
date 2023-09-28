from pydantic import BaseModel
from typing import List, Optional
import requests
import json


def generate_variations(openai_api_key, human_usage_example):
    url = "https://api.openai.com/v1/chat/completions"
    # Prepare the request payload for generating variations
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
        'Authorization': f'Bearer {openai_api_key}'
    }
    # Send a POST request to OpenAI API to generate variations
    response = requests.request("POST", url, headers=headers, data=payload)
    # Extract and format the variations from the response
    choices = response.json().get("choices", [])[0].get("message", {}).get(
        "content")
    res = []
    for choice in choices.splitlines():
        if len(choice) >= 2 and choice[0].isdigit() and choice[1] == '.':
            res.append(choice[2:].strip())
        else:
            res.append(choice)
    return res


# Define a Pydantic BaseModel for the 'Path' class
class Path(BaseModel):
    path: str
    method: str


# Define a Pydantic BaseModel for generating test cases
class GenerateTestCase(BaseModel):
    openplugin_manifest_url: str
    openai_api_key: str
    for_paths: Optional[List[Path]] = []

    def generate_test_cases(self):
        # Retrieve the JSON data from the specified URL
        openplugin_manifest_json = requests.get(self.openplugin_manifest_url).json()
        # Extract plugin operations from the JSON data
        plugin_operations = openplugin_manifest_json.get("plugin_operations", {})
        # Iterate through paths and methods
        for path in plugin_operations.keys():
            for method in plugin_operations.get(path):
                if self.for_paths and len(self.for_paths) > 0:
                    if not any([path == p.path and method == p.method for p in
                                self.for_paths]):
                        continue
                human_usage_examples = plugin_operations.get(path).get(method).get(
                    "human_usage_examples", [])
                more_examples = []
                # Generate variations for each human usage example
                for example in human_usage_examples:
                    more_examples.extend(
                        generate_variations(self.openai_api_key, example))
                human_usage_examples.extend(more_examples)
        return openplugin_manifest_json
