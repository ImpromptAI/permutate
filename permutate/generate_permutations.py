import os
from typing import List, Optional

import boto3
import requests
from dotenv import load_dotenv
from pydantic import BaseModel

from permutate import Config, JobRequest, PermutationConfig, Plugin, TestCase
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
        permutation_config = self.gen_permutation_config()
        test_cases = self.gen_test_variations(
            openplugin_manifest_json, server_endpoint
        )
        name = (
            f'{openplugin_manifest_json.get("name", "").replace(" ", "_")}'
            f"_test".lower()
        )
        operations: List[str] = []

        for ops in openplugin_manifest_json.get("plugin_operations", {}).keys():
            for method in (
                openplugin_manifest_json.get("plugin_operations", {})
                .get(ops, {})
                .keys()
            ):
                operations.append(f"{method} {ops}")
        response = JobRequest(
            version="1.1.0",
            name=name,
            config=Config(
                openplugin_api_key=None,
                use_openplugin_library=True,
                openai_api_key=None,
                auto_translate_to_languages=[],
                tool_selector_endpoint=None,
            ),
            test_plugin=Plugin(manifest_url=self.request.openplugin_manifest_url),
            permutation_config=permutation_config,
            test_cases=test_cases,
            operations=operations,
        )
        return response

    def gen_test_variations(self, openplugin_manifest_json, server_endpoint):
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
                    for ex in generate_variations(
                        self.request.openai_api_key, example
                    ):
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

    def gen_permutation_config(self) -> PermutationConfig:
        return PermutationConfig(
            strategies=["OAI Functions"],
            llms=[
                {
                    "provider": "OpenAI",
                    "model": "gpt-4",
                    "temperature": 0.4,
                    "max_tokens": 1024,
                    "top_p": 1,
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                }
            ],
        )


"""
request = GeneratePermutationsRequest(
    openplugin_manifest_url="https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json")
obj = GeneratePermutations(request=request)
response=obj.gen()
print(response.json())
"""
