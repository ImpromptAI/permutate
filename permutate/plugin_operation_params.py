import traceback
from typing import Any, Dict

import requests


def get_plugin_operation_params(url: str):
    try:
        openapi_doc_json = requests.get(url).json()

        refs = {}
        schemas = openapi_doc_json.get("components", {}).get("schemas")
        if schemas:
            for key in schemas:
                refs[key] = schemas[key]

        result_map: Dict[Any, Any] = {}
        for path in openapi_doc_json["paths"]:
            result_map[path] = {}
            for method in openapi_doc_json["paths"][path]:
                if method == "get":
                    if openapi_doc_json["paths"][path][method].get("parameters"):
                        parameters = openapi_doc_json["paths"][path][method][
                            "parameters"
                        ]
                        for prop in parameters:
                            prop["in"] = "query"
                            # flatten schema
                            if prop.get("schema"):
                                for key in prop["schema"]:
                                    prop[key] = prop["schema"][key]
                                del prop["schema"]
                        result_map[path][method] = parameters
                elif method == "post":
                    ref = (
                        openapi_doc_json["paths"][path][method]
                        .get("requestBody", {})
                        .get("content", {})
                        .get("application/json", {})
                        .get("schema", {})
                        .get("$ref")
                    )
                    if ref:
                        props = refs[ref.split("/")[-1]]["properties"]
                        params = []
                        if isinstance(props, dict):
                            for key in props.keys():
                                props[key]["name"] = key
                                props[key]["in"] = "body"
                                # check if required
                                if (
                                    refs[ref.split("/")[-1]].get("required")
                                    and key in refs[ref.split("/")[-1]]["required"]
                                ):
                                    props[key]["required"] = True
                                else:
                                    props[key]["required"] = False
                                params.append(props[key])
                        result_map[path][method]=params
        return result_map
    except Exception:
        traceback.print_exc()
