import os
from itertools import combinations
from typing import Optional

import boto3
import requests
from dotenv import load_dotenv
from pydantic import BaseModel

from permutate import Config, JobRequest, Permutation, Plugin, TestCase
from permutate.generate_test_cases import generate_variations

load_dotenv()
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")


class GeneratePermutationsRequest(BaseModel):
    openplugin_manifest_url: str
    openai_api_key: Optional[str]
    save_to_s3: bool = False
    plugin_group_manifest_urls: list = []


class GeneratePermutations(BaseModel):
    request: GeneratePermutationsRequest

    def gen_s3(self) -> dict:
        openplugin_manifest_json = requests.get(
            self.request.openplugin_manifest_url
        ).json()
        response = self.gen_variations(openplugin_manifest_json)
        # Add to S3 Bucket
        s3 = boto3.client(
            "s3",
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
        )
        name = f"{openplugin_manifest_json.get('name')}/{response.name}.json"
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=name,
            Body=response.json(),
            ContentType="text/json",
            ACL="public-read",
        )
        # results = s3.get_object(Bucket=S3_BUCKET_NAME, Key=name)
        full_url = s3.generate_presigned_url(
            "get_object", Params={"Bucket": S3_BUCKET_NAME, "Key": name}
        )
        public_url = full_url.split("?")[0]
        return {"s3_url": public_url}

    def gen(self) -> JobRequest:
        openplugin_manifest_json = requests.get(
            self.request.openplugin_manifest_url
        ).json()
        return self.gen_variations(openplugin_manifest_json)

    def gen_variations(self, openplugin_manifest_json) -> JobRequest:
        opeapi_doc_json = requests.get(
            openplugin_manifest_json.get("openapi_doc_url")
        ).json()
        server_endpoint = None
        if (
            opeapi_doc_json
            and opeapi_doc_json.get("servers")
            and len(opeapi_doc_json.get("servers")) > 0
        ):
            server_endpoint = opeapi_doc_json.get("servers")[0].get("url")
        plugin_groups = self.gen_plugin_groups()
        permutations = self.gen_permutations(plugin_groups)
        test_cases = self.gen_test_variations(openplugin_manifest_json, server_endpoint)
        name = (
            f'{openplugin_manifest_json.get("name", "").replace(" ", "_")}'
            f"_test".lower()
        )
        response = JobRequest(
            version="1.1.0",
            name=name,
            config=Config(),
            test_plugin=Plugin(manifest_url=self.request.openplugin_manifest_url),
            plugin_groups=plugin_groups,
            permutations=permutations,
            test_cases=test_cases,
        )
        return response

    def gen_plugin_groups(self) -> list:
        plugins = [self.request.openplugin_manifest_url]
        plugins.extend(self.request.plugin_group_manifest_urls)
        all_combinations = []
        index = 1
        for r in range(1, len(plugins) + 1):
            for pl in list(combinations(plugins, r)):
                all_combinations.append(
                    {
                        "name": f"Plugin Group {index}",
                        "plugins": [{"manifest_url": k} for k in pl],
                    }
                )
                index += 1
        return all_combinations

    def gen_test_variations(self, openplugin_manifest_json, server_endpoint) -> list:
        test_cases = []
        plugin_operations = openplugin_manifest_json.get("plugin_operations", {})
        for path in plugin_operations.keys():
            complete_endpoint = path
            if server_endpoint:
                complete_endpoint = server_endpoint + path
            for method in plugin_operations.get(path):
                index = 1
                human_usage_examples = (
                    plugin_operations.get(path)
                    .get(method)
                    .get("human_usage_examples", [])
                )
                for example in human_usage_examples:
                    test_cases.append(
                        TestCase(
                            name=f"test-case {index}",
                            prompt=example,
                            expected_response=None,
                            expected_plugin_used=self.request.openplugin_manifest_url,
                            expected_api_used=complete_endpoint,
                            expected_method=method,
                            expected_parameters=None,
                        )
                    )
                    index = index + 1
                    for ex in generate_variations(self.request.openai_api_key, example):
                        test_cases.append(
                            TestCase(
                                name=f"test-case {index}",
                                prompt=ex,
                                expected_response=None,
                                expected_plugin_used=self.request.openplugin_manifest_url,
                                expected_api_used=complete_endpoint,
                                expected_method=method,
                                expected_parameters=None,
                            )
                        )
                        index = index + 1
                        # TODO remove

            return test_cases

    def gen_permutations(self, plugin_groups) -> list:
        permutations = []
        for pg in plugin_groups:
            permutations.append(
                Permutation(
                    name="permutation 1",
                    llm={
                        "provider": "OpenAIChat",
                        "model_name": "gpt-3.5-turbo",
                        "supported_max_tokens": 4096,
                        "temperature": 0,
                        "max_tokens": 1024,
                        "top_p": 1,
                        "frequency_penalty": 0,
                        "presence_penalty": 0,
                        "n": 1,
                        "best_of": 1,
                    },
                    tool_selector={
                        "provider": "OpenAI",
                        "pipeline_name": "default",
                        "plugin_group_name": pg.get("name"),
                    },
                )
            )
            permutations.append(
                Permutation(
                    name="permutation 2",
                    llm={
                        "provider": "OpenAIChat",
                        "model_name": "gpt-4",
                        "supported_max_tokens": 4096,
                        "temperature": 0,
                        "max_tokens": 2048,
                        "top_p": 1,
                        "frequency_penalty": 0,
                        "presence_penalty": 0,
                        "n": 1,
                        "best_of": 1,
                    },
                    tool_selector={
                        "provider": "OpenAI",
                        "pipeline_name": "default",
                        "plugin_group_name": pg.get("name"),
                    },
                )
            )
            permutations.append(
                Permutation(
                    name="permutation 3",
                    llm={
                        "provider": "OpenAIChat",
                        "model_name": "gpt-3.5-turbo",
                        "supported_max_tokens": 4096,
                        "temperature": 0.5,
                        "max_tokens": 1024,
                        "top_p": 1,
                        "frequency_penalty": 0,
                        "presence_penalty": 0,
                        "n": 1,
                        "best_of": 1,
                    },
                    tool_selector={
                        "provider": "OpenAI",
                        "pipeline_name": "default",
                        "plugin_group_name": pg.get("name"),
                    },
                )
            )
            permutations.append(
                Permutation(
                    name="permutation 4",
                    llm={
                        "provider": "OpenAIChat",
                        "model_name": "gpt-4",
                        "supported_max_tokens": 4096,
                        "temperature": 0.5,
                        "max_tokens": 2048,
                        "top_p": 1,
                        "frequency_penalty": 0,
                        "presence_penalty": 0,
                        "n": 1,
                        "best_of": 1,
                    },
                    tool_selector={
                        "provider": "OpenAI",
                        "pipeline_name": "default",
                        "plugin_group_name": pg.get("name"),
                    },
                )
            )
        return permutations


"""
request = GeneratePermutationsRequest(
    openplugin_manifest_url="https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json")
obj = GeneratePermutations(request=request)
response=obj.gen()
print(response.json())
"""
