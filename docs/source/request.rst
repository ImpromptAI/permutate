Request
============


.. tabs::

  .. tab:: YAML

    .. code-block:: yaml

        version: 1.1.0
        name: klarna_plugin_test
        config:
          tool_selector_endpoint: http://localhost:8006
          openplugin_api_key:
          auto_translate_to_languages:
            - English
            - Spanish
        test_plugin:
          manifest_url: https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json
        plugin_groups:
          - plugin_group:
            name: my_group1
            plugins:
              - plugin:
                manifest_url: https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json
          - plugin_group:
            name: my_group2
            plugins:
              - plugin:
                manifest_url: https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json
              - plugin:
                manifest_url: https://assistant-management-data.s3.amazonaws.com/Imprompt_Web_Search.json
        permutations:
          - permutation:
            name: permutation1
            llm:
              provider: OpenAIChat
              model_name: gpt-3.5-turbo-0613
              temperature: 0
              max_tokens: 1024
              top_p: 1
              frequency_penalty: 0
              presence_penalty: 0
              n: 1
              best_of: 1
            tool_selector:
              provider: OpenAI
              pipeline_name: default
              plugin_group_name: my_group1
          - permutation:
            name: permutation2
            llm:
              provider: OpenAIChat
              model_name: gpt-3.5-turbo-0613
              temperature: 0
              max_tokens: 1024
              top_p: 1
              frequency_penalty: 0
              presence_penalty: 0
              n: 1
              best_of: 1
            tool_selector:
              provider: Imprompt
              pipeline_name: default
              plugin_group_name: my_group1
          - permutation:
            name: permutation3
            llm:
              provider: OpenAIChat
              model_name: gpt-3.5-turbo-0613
              temperature: 0
              max_tokens: 1024
              top_p: 1
              frequency_penalty: 0
              presence_penalty: 0
              n: 1
              best_of: 1
            tool_selector:
              provider: Langchain
              pipeline_name: zero-shot-react-description
              plugin_group_name: my_group1
        test_cases:
          - test_case:
            name: test1
            type: plugin_selector
            prompt: Show me 5 T shirts from Klarna
            expected_plugin_used: https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json
            expected_api_used: https://www.klarna.com/us/shopping/public/openai/v0/products
            expected_method: get
          - test_case:
            name: test2
            type: api_signature_selector
            prompt: Show me 5 T shirts from Klarna
            expected_plugin_used: https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json
            expected_api_used: https://www.klarna.com/us/shopping/public/openai/v0/products
            expected_method: get
            expected_parameters:
              q: T shirt
              size: 5

  .. tab:: JSON

    .. code-block:: json

        {
          "version": "1.1.0",
          "name": "klarna_plugin_test",
          "config": {
            "tool_selector_endpoint": "http://localhost:8006",
            "openplugin_api_key": null,
            "auto_translate_to_languages": [
              "English",
              "Spanish"
            ]
          },
          "test_plugin": {
            "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
          },
          "plugin_groups": [
            {
              "plugin_group": null,
              "name": "my_group1",
              "plugins": [
                {
                  "plugin": null,
                  "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
                }
              ]
            },
            {
              "plugin_group": null,
              "name": "my_group2",
              "plugins": [
                {
                  "plugin": null,
                  "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
                },
                {
                  "plugin": null,
                  "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Imprompt_Web_Search.json"
                }
              ]
            }
          ],
          "permutations": [
            {
              "permutation": null,
              "name": "permutation1",
              "llm": {
                "provider": "OpenAIChat",
                "model_name": "gpt-3.5-turbo-0613",
                "temperature": 0,
                "max_tokens": 1024,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "n": 1,
                "best_of": 1
              },
              "tool_selector": {
                "provider": "OpenAI",
                "pipeline_name": "default",
                "plugin_group_name": "my_group1"
              }
            },
            {
              "permutation": null,
              "name": "permutation2",
              "llm": {
                "provider": "OpenAIChat",
                "model_name": "gpt-3.5-turbo-0613",
                "temperature": 0,
                "max_tokens": 1024,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "n": 1,
                "best_of": 1
              },
              "tool_selector": {
                "provider": "Imprompt",
                "pipeline_name": "default",
                "plugin_group_name": "my_group1"
              }
            },
            {
              "permutation": null,
              "name": "permutation3",
              "llm": {
                "provider": "OpenAIChat",
                "model_name": "gpt-3.5-turbo-0613",
                "temperature": 0,
                "max_tokens": 1024,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "n": 1,
                "best_of": 1
              },
              "tool_selector": {
                "provider": "Langchain",
                "pipeline_name": "zero-shot-react-description",
                "plugin_group_name": "my_group1"
              }
            }
          ],
          "test_cases": [
            {
              "test_case": null,
              "name": "test1",
              "type": "plugin_selector",
              "prompt": "Show me 5 T shirts from Klarna",
              "expected_plugin_used": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json",
              "expected_api_used": "https://www.klarna.com/us/shopping/public/openai/v0/products",
              "expected_method": "get"
            },
            {
              "test_case": null,
              "name": "test2",
              "type": "api_signature_selector",
              "prompt": "Show me 5 T shirts from Klarna",
              "expected_plugin_used": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json",
              "expected_api_used": "https://www.klarna.com/us/shopping/public/openai/v0/products",
              "expected_method": "get",
              "expected_parameters": {
                "q": "T shirt",
                "size": 5
              }
            }
          ]
        }