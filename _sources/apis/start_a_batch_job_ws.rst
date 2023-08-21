===================================
Start a batch job with websockets
===================================

The API endpoint: {{SERVER_ENDPOINT}}/api/ws/start-batch-job


To learn about building request body, see :ref:`request-label`.

Request
=========

.. tabs::

  .. tab:: REST

    .. code-block:: sh

        API Endpoint: {{SERVER_ENDPOINT}}/api/ws/start-batch-job

        Method: WebSocket

        Message: {
                  "version": "1.1.0",
                  "name": "klarna_plugin_test",
                  "config": {
                    "openplugin_api_key": "",
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
                      "name": "my_group1",
                      "plugins": [
                        {
                          "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
                        }
                      ]
                    },
                    {
                      "name": "my_group2",
                      "plugins": [
                        {
                          "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
                        },
                        {
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

Response
============

As the job progresses, the WebSocket server sends result of each permutation run, including result and any critical messages or errors.

The response is a websocket message with the following format:

.. code-block:: json

    {
        "permutation_name": "permutation2",
        "permutation_summary": "OpenAIChat[gpt-3.5-turbo-0613] - Imprompt[default]",
        "test_type": "plugin_selector",
        "test_case_name": "test1",
        "is_run_completed": true,
        "language": "English",
        "prompt": "Show me 5 T shirts from Klarna",
        "final_output": null,
        "match_score": 0.0,
        "is_plugin_detected": true,
        "is_plugin_operation_found": true,
        "is_plugin_parameter_mapped": false,
        "plugin_name": "Klarna Shopping",
        "plugin_operation": "https://www.klarna.com/us/shopping/public/openai/v0/products",
        "plugin_parameters_mapped": null,
        "parameter_mapped_percentage": 0.0,
        "response_time_sec": 1.96,
        "total_llm_tokens_used": 1178,
        "llm_api_cost": 0.0
    }