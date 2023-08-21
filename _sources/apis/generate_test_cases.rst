========================
Generate test cases
========================

The API to generate test cases for a plugin. The test cases are generated using the existing human usage examples added in the openplugin manifest file.

The API endpoint: {{SERVER_ENDPOINT}}/api/generate-test-cases

Request
=========

.. tabs::

  .. tab:: curl

    .. code-block:: sh

        curl --location 'localhost:8989/api/generate-test-cases' \
                --header 'Content-Type: application/json' \
                --data '{
                    "openplugin_manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json",
                    "openai_api_key":"",
                    "for_paths":[
                        {
                            "path":"/public/openai/v0/products",
                            "method":"get"
                        }
                    ]
                }'

  .. tab:: python

    .. code-block:: python

        import requests
        import json

        url = "localhost:8989/api/generate-test-cases"

        payload = json.dumps({
          "openplugin_manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json",
          "openai_api_key": "",
          "for_paths": [
            {
              "path": "/public/openai/v0/products",
              "method": "get"
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

        API Endpoint: {{SERVER_ENDPOINT}}/api/generate-test-cases

        Method: POST

        Headers: {
          'x-api-key': 'your-api-key'
          'Content-Type': 'application/json'
        }

        Body: {
              "openplugin_manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json",
              "openai_api_key": "",
              "for_paths": [
                {
                  "path": "/public/openai/v0/products",
                  "method": "get"
                }
              ]
            }


Response
============

.. code-block:: json

    {
        "auth": {
            "type": "none"
        },
        "name": "Klarna Shopping",
        "logo_url": "https://www.klarna.com/assets/sites/5/2020/04/27143923/klarna-K-150x150.jpg",
        "description": "Assistant uses the Klarna plugin to get relevant product suggestions for any shopping or product discovery purpose.",
        "contact_email": "openai-products@klarna.com",
        "legal_info_url": "https://www.klarna.com/us/legal/",
        "schema_version": "v1",
        "openapi_doc_url": "https://www.klarna.com/us/shopping/public/openai/v0/api-docs/",
        "plugin_operations": {
            "/public/openai/v0/products": {
                "get": {
                    "human_usage_examples": [
                        "Show me some T Shirts.",
                        "Show me some pants.",
                        "Show me winter jackets for men.",
                        "Can you please display a variety of T-shirts for me to choose from?",
                        "I'm interested in viewing a collection of T-shirts. Could you please show me some options?",
                        "I'd like to see a selection of T-shirts. Can you show me what you have available?",
                        "Can you bring up a few examples of T-shirts for me to browse?",
                        "Could you show me some different styles of T-shirts?",
                        "Can you please display a selection of pants?",
                        "I'm looking for pants, could you show me some options?",
                        "Can you provide me with a variety of pants?",
                        "Please show me different styles of pants.",
                        "I need to see different types of pants, could you help me?",
                        "Can you please display a selection of men's winter jackets?",
                        "I'm in need of some ideas for winter jackets for men, can you show me some options?",
                        "I want to see what kind of winter jackets are available for men, can you show me a range of choices?",
                        "Could you please show me a variety of winter jackets specifically designed for men?",
                        "I'm looking for men's winter jackets, could you help me find some options to consider?"
                    ],
                    "plugin_cleanup_helpers": [
                        "Use markdown",
                        "Summarize and list the products"
                    ],
                    "plugin_signature_helpers": []
                }
            }
        }
    }


Body Parameters
==================

.. code-block:: json

    {
      "openplugin_manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json",
      "openai_api_key": "",
      "for_paths": [
        {
          "path": "/public/openai/v0/products",
          "method": "get"
        }
      ]
    }

**openplugin_manifest_url:** The url of the openplugin manifest file. This file contains the information about the plugin.

**openai_api_key:** The openai api key. This is required to generate the test cases.

**for_paths:** The list of paths for which the test cases should be generated. The path should match the path in openapi documentation. The method should be one of get, post, put, delete, patch, options, head.