========================
Interactive run
========================

The API to run the test cases interactively.

The API endpoint: {{SERVER_ENDPOINT}}/api/interactive-run

To learn about building request body, see :ref:`request-label`.


Request
=========

.. tabs::

  .. tab:: curl

    .. code-block:: sh

        curl --location 'localhost:8989/api/interactive-run' \
            --header 'Content-Type: application/json' \
            --data '{
                "config":{

                },
                "plugin": {
                    "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
                },
                "plugin_group": {
                    "plugin_group": null,
                    "name": "my_group1",
                    "plugins": [{
                            "plugin": null,
                            "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
                        },
                        {
                            "plugin": null,
                            "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Imprompt_Web_Search.json"
                        }
                    ]
                },
                "permutation": {
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
                "test_case": {
                    "test_case": null,
                    "name": "test1",
                    "type": "plugin_selector",
                    "prompt": "Show me 5 T shirts from Klarna",
                    "expected_plugin_used": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json",
                    "expected_api_used": "https://www.klarna.com/us/shopping/public/openai/v0/products",
                    "expected_method": "get"
                }
            }'

  .. tab:: python

    .. code-block:: python

        import requests
        import json

        url = "localhost:8989/api/interactive-run"

        payload = json.dumps({
          "config": {},
          "plugin": {
            "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
          },
          "plugin_group": {
            "plugin_group": None,
            "name": "my_group1",
            "plugins": [
              {
                "plugin": None,
                "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
              },
              {
                "plugin": None,
                "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Imprompt_Web_Search.json"
              }
            ]
          },
          "permutation": {
            "permutation": None,
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
          "test_case": {
            "test_case": None,
            "name": "test1",
            "type": "plugin_selector",
            "prompt": "Show me 5 T shirts from Klarna",
            "expected_plugin_used": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json",
            "expected_api_used": "https://www.klarna.com/us/shopping/public/openai/v0/products",
            "expected_method": "get"
          }
        })
        headers = {
          'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)


  .. tab:: REST

    .. code-block:: sh

        API Endpoint: {{SERVER_ENDPOINT}}/api/interactive-run

        Method: POST

        Headers: {
          'x-api-key': 'your-api-key'
          'Content-Type': 'application/json'
        }

        Body: {
                "config":{

                },
                "plugin": {
                    "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
                },
                "plugin_group": {
                    "plugin_group": null,
                    "name": "my_group1",
                    "plugins": [{
                            "plugin": null,
                            "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
                        },
                        {
                            "plugin": null,
                            "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Imprompt_Web_Search.json"
                        }
                    ]
                },
                "permutation": {
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
                "test_case": {
                    "test_case": null,
                    "name": "test1",
                    "type": "plugin_selector",
                    "prompt": "Show me 5 T shirts from Klarna",
                    "expected_plugin_used": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json",
                    "expected_api_used": "https://www.klarna.com/us/shopping/public/openai/v0/products",
                    "expected_method": "get"
                }
            }


Response
============

.. code-block:: json

    {
        "job_name": "interactive-run-1.0-2023-08-18",
        "started_on": "2023-08-18T15:25:32.744928",
        "completed_on": "2023-08-18T15:25:38.426335",
        "test_plugin": {
            "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
        },
        "permutations": [
            {
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
            }
        ],
        "summary": {
            "total_test_cases": 1,
            "failed_cases": 0,
            "language": "English",
            "overall_accuracy": 0.0,
            "accuracy_step_a": 1.0,
            "accuracy_step_b": 1.0,
            "accuracy_step_c": 0.0,
            "total_run_time": 3.07,
            "average_response_time_sec": 3.07,
            "total_llm_tokens_used": 588,
            "average_llm_tokens_used": 588,
            "total_llm_api_cost": 0.0
        },
        "details": [
            {
                "permutation_name": "permutation1",
                "permutation_summary": "OpenAIChat[gpt-3.5-turbo-0613] - OpenAI[default]",
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
                "response_time_sec": 3.07,
                "total_llm_tokens_used": 588,
                "llm_api_cost": 0.0
            }
        ],
        "output_directory": null
    }