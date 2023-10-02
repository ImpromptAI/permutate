import traceback

import requests


def get_plugin_operation_params(url: str):
    try:
        openplugin_manifest_json = requests.get(url).json()
        openapi_doc_url = openplugin_manifest_json["openapi_doc_url"]
        openapi_doc_json = requests.get(openapi_doc_url).json()

        refs = {}
        schemas = openapi_doc_json.get("components", {}).get("schemas")
        if schemas:
            for key in schemas:
                refs[key] = schemas[key]

        param_map = {}
        for path in openapi_doc_json["paths"]:
            for method in openapi_doc_json["paths"][path]:
                if method == "get":
                    if openapi_doc_json["paths"][path][method].get("parameters"):
                        parameters = openapi_doc_json["paths"][path][method][
                            "parameters"
                        ]
                        for prop in parameters:
                            prop["in"] = "query"
                            if prop.get("title"):
                                prop["name"] = prop.get("title")
                        param_map[f"{path}_{method}"] = parameters
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
                                params.append(props[key])
                        param_map[f"{path}_{method}"] = params
        result_map = {}

        for operation in openplugin_manifest_json["plugin_operations"]:
            result_map[operation] = {}
            for method in openplugin_manifest_json["plugin_operations"][operation]:
                result_map[operation][method] = param_map.get(
                    f"{operation}_{method}", []
                )
        return result_map
    except Exception:
        traceback.print_exc()
