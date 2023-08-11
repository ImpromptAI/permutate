Request
============

Permutate takes a request in the form of a YAML or JSON file. The request contains the following fields:


**1. Name**

.. tabs::

  .. tab:: Fields

    .. list-table::
       :widths: 20 20 60
       :header-rows: 1

       * - Field
         - Type
         - Description
       * - name
         - string
         - The name of the request

  .. tab:: YAML

    .. code-block:: yaml

        name: klarna_plugin_test

  .. tab:: JSON

    .. code-block:: json

        {
          "name": "klarna_plugin_test"
        }

**2. Test Plugin**

The test plugin is the plugin that will be used to test the permutations. This plugin will be used to generate the test cases.

.. tabs::

  .. tab:: Fields

    .. list-table::
       :widths: 20 20 60
       :header-rows: 1

       * - Field
         - Type
         - Description
       * - manifest_url
         - string
         - The manifest url of the test plugin

  .. tab:: YAML

    .. code-block:: yaml

        test_plugin:
          manifest_url: https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json

  .. tab:: JSON

    .. code-block:: json

        {
          "test_plugin": {
            "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
          }
        }

**3. Config**

The config contains the configuration for the test suite.

.. tabs::

  .. tab:: Fields

    .. list-table::
       :widths: 20 20 60
       :header-rows: 1

       * - Field
         - Type
         - Description
       * - tool_selector_endpoint
         - string
         - The endpoint of the tool selector
       * - openplugin_api_key
         - string
         - The openplugin api key
       * - auto_translate_to_languages
         - list of strings
         - The auto translate to languages is a list of languages that the test cases will be translated to. This is used to translate the test cases to different languages.

  .. tab:: YAML

    .. code-block:: yaml

        config:
          tool_selector_endpoint: http://localhost:8006
          openplugin_api_key:
          auto_translate_to_languages:
            - English
            - Spanish

  .. tab:: JSON

    .. code-block:: json

        {
          "config": {
            "tool_selector_endpoint": "http://localhost:8006",
            "openplugin_api_key": "",
            "auto_translate_to_languages": [
              "English",
              "Spanish"
            ]
          }
        }

**4. Plugin Groups**

The plugin groups are the groups of plugins that will be used to test the permutations. The plugin groups are used to test the tool selector.

.. tabs::

  .. tab:: Fields

    .. list-table::
       :widths: 20 20 60
       :header-rows: 1

       * - Field
         - Type
         - Description
       * - plugin_group
         - list of plugin groups
         - The plugin groups that will be used to test the permutations
       * - name
         - string
         - The name of the plugin group
       * - plugins
         - list of plugins
         - The plugins that will be used to test the permutations
       * - plugin
         - list of plugins
         - The plugins that will be used to test the permutations
       * - manifest_url
         - string
         - The manifest url of the plugin

  .. tab:: YAML

    .. code-block:: yaml

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

  .. tab:: JSON

    .. code-block:: json

        {
          "plugin_groups": [
            {
              "plugin_group": {
                "name": "my_group1",
                "plugins": [
                  {
                    "plugin": {
                      "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
                    }
                  }
                ]
              }
            },
            {
              "plugin_group": {
                "name": "my_group2",
                "plugins": [
                  {
                    "plugin": {
                      "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
                    }
                  },
                  {
                    "plugin": {
                      "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Imprompt_Web_Search.json"
                    }
                  }
                ]
              }
            }
          ]
        }


Sample Request
=================


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