from permutate.plugin_operation_params import get_plugin_operation_params


def test_get_plugin_operation_params() -> None:
    response = get_plugin_operation_params(
        "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
    )
    print(response)
