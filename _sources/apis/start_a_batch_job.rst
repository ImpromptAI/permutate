========================
Start a batch job
========================

The API to start a batch job. The batch job will run all the test cases and permutations and return the results.

The API endpoint: {{SERVER_ENDPOINT}}/api/start-job

To learn about building request body, see :ref:`request-label`.

Request
=========

.. tabs::

  .. tab:: curl

    .. code-block:: sh

        curl --location 'http://localhost:8989/api/start-job' \
        --header 'Content-Type: application/json' \
        --data '{
          "version": "1.1.0",
          "name": "klarna_plugin_test",
          "config": {
            "tool_selector_endpoint": None,
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
        }'

  .. tab:: python

    .. code-block:: python

        import requests
        import json

        url = "http://localhost:8989/api/start-job"

        payload = json.dumps({
          "version": "1.1.0",
          "name": "klarna_plugin_test",
          "config": {
            "tool_selector_endpoint":None,
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
            {
              "permutation": None,
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
              "permutation": None,
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
              "test_case": None,
              "name": "test1",
              "type": "plugin_selector",
              "prompt": "Show me 5 T shirts from Klarna",
              "expected_plugin_used": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json",
              "expected_api_used": "https://www.klarna.com/us/shopping/public/openai/v0/products",
              "expected_method": "get"
            },
            {
              "test_case": None,
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
        })
        headers = {
          'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)



  .. tab:: REST

    .. code-block:: sh

        API Endpoint: {{SERVER_ENDPOINT}}/api/start-job

        Method: POST

        Headers: {
          'x-api-key': 'your-api-key'
          'Content-Type': 'application/json'
        }

        Body: {
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

.. code-block:: json

    {
        "job_name": "klarna_plugin_test-1.1.0-2023-08-18",
        "started_on": "2023-08-18T16:02:55.314867",
        "completed_on": "2023-08-18T16:03:24.853418",
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
            },
            {
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
        "summary": {
            "total_test_cases": 3,
            "failed_cases": 0,
            "language": "English",
            "overall_accuracy": 0.0,
            "accuracy_step_a": 3.0,
            "accuracy_step_b": 3.0,
            "accuracy_step_c": 0.0,
            "total_run_time": 27.19,
            "average_response_time_sec": 9.06,
            "total_llm_tokens_used": 9278,
            "average_llm_tokens_used": 3092,
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
                "response_time_sec": 1.39,
                "total_llm_tokens_used": 412,
                "llm_api_cost": 0.0
            },
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
                "response_time_sec": 2.18,
                "total_llm_tokens_used": 1178,
                "llm_api_cost": 0.0
            },
            {
                "permutation_name": "permutation3",
                "permutation_summary": "OpenAIChat[gpt-3.5-turbo-0613] - Langchain[zero-shot-react-description]",
                "test_type": "plugin_selector",
                "test_case_name": "test1",
                "is_run_completed": true,
                "language": "English",
                "prompt": "Show me 5 T shirts from Klarna",
                "final_output": "Here are 5 T shirts from Klarna:\n1. Lacoste Plain T-shirts 3-pack - [Link](https://www.klarna.com/us/shopping/pl/cl10001/3202043025/Clothing/Lacoste-Plain-T-shirts-3-pack/?utm_source=openai&ref-site=openai_plugin)\n2. Nike JDI Tshirt T-shirts Bomuld hos Magasin - [Link](https://www.klarna.com/us/shopping/pl/cl10001/3202152606/Clothing/Nike-JDI-Tshirt-T-shirts-Bomuld-hos-Magasin/?utm_source=openai&ref-site=openai_plugin)\n3. Nautica Mens Crewneck T-Shirts, 5-Pack white - [Link](https://www.klarna.com/us/shopping/pl/cl10001/3206204426/Clothing/Nautica-Mens-Crewneck-T-Shirts-5-Pack-white/?utm_source=openai&ref-site=openai_plugin)\n4. Under Armour Men's Tactical Tech Long Sleeve T-shirts - [Link](https://www.klarna.com/us/shopping/pl/cl10001/3201831193/Clothing/Under-Armour-Men-s-Tactical-Tech-Long-Sleeve-T-shirts/?utm_source=openai&ref-site=openai_plugin)\n5. Hanes Boy's Ultimate Lightweight T-shirts 5-Pack - Assorted (BUBCR5) - [Link](https://www.klarna.com/us/shopping/pl/cl359/3201157848/Children-s-Clothing/Hanes-Boy-s-Ultimate-Lightweight-T-shirts-5-Pack-Assorted-%28BUBCR5%29/?utm_source=openai&ref-site=openai_plugin)",
                "match_score": 0.0,
                "is_plugin_detected": true,
                "is_plugin_operation_found": true,
                "is_plugin_parameter_mapped": false,
                "plugin_name": "Klarna Shopping",
                "plugin_operation": "https://www.klarna.com/us/shopping/public/openai/v0/products",
                "plugin_parameters_mapped": null,
                "parameter_mapped_percentage": 0.0,
                "response_time_sec": 23.62,
                "total_llm_tokens_used": 7688,
                "llm_api_cost": 0.0
            }
        ],
        "output_directory": null
    }