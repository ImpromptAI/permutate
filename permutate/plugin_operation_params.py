import requests


def get_plugin_operation_params(url: str):
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
                    param_map[f"{path}_{method}"] = openapi_doc_json["paths"][path][
                        method
                    ]["parameters"]
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
                    param_map[f"{path}_{method}"] = refs[ref.split("/")[-1]][
                        "properties"
                    ]
    result_map = {}

    for operation in openplugin_manifest_json["plugin_operations"]:
        result_map[operation] = {}
        for method in openplugin_manifest_json["plugin_operations"][operation]:
            result_map[operation][method] = param_map.get(
                f"{operation}_{method}", []
            )
    return result_map
