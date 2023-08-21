========================
Get Permutations
========================

List of APIs to get permutations for different use cases.

Get LLM Permutations
========================

The API endpoint: {{SERVER_ENDPOINT}}/api/llm-permutations

Request
=========

.. tabs::

  .. tab:: curl

    .. code-block:: sh

        curl --location 'localhost:8989/api/llm-permutations'

  .. tab:: python

    .. code-block:: python

        import requests
        url = "localhost:8989/api/llm-permutations"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)

  .. tab:: REST

    .. code-block:: sh

        API Endpoint: {{SERVER_ENDPOINT}}/api/llm-permutation

        Method: GET

        Headers: {
          'x-api-key': 'your-api-key'
          'Content-Type': 'application/json'
        }

Response
============

.. code-block:: json

    [
        {
            "provider": "OpenAIChat",
            "model_name": "gpt-3.5-turbo-0613",
            "temperature": 0,
            "max_tokens": 1024,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "n": 1,
            "best_of": 1
        }
    ]

Get Tool Selector Permutations
=================================

The API endpoint: {{SERVER_ENDPOINT}}/api/tool-selector-permutations

Request
=========

.. tabs::

  .. tab:: curl

    .. code-block:: sh

        curl --location 'localhost:8989/api/tool-selector-permutations'

  .. tab:: python

    .. code-block:: python

        import requests
        url = "localhost:8989/api/tool-selector-permutations"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)

  .. tab:: REST

    .. code-block:: sh

        API Endpoint: {{SERVER_ENDPOINT}}/api/tool-selector-permutations

        Method: GET

        Headers: {
          'x-api-key': 'your-api-key'
          'Content-Type': 'application/json'
        }

Response
============

.. code-block:: json

    [
        {
            "provider": "OpenAI",
            "pipeline_name": "default"
        },
        {
            "provider": "Langchain",
            "pipeline_name": "zero-shot-react-description"
        },
        {
            "provider": "Imprompt",
            "pipeline_name": "default"
        }
    ]

Get Plugin Group Permutations
=================================

The API endpoint: {{SERVER_ENDPOINT}}/api/plugin-group-permutations

Request
=========

.. tabs::

  .. tab:: curl

    .. code-block:: sh

        curl --location 'localhost:8989/api/plugin-group-permutations?plugin_manifest=https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json&plugin_manifest=https://assistant-management-data.s3.amazonaws.com/Imprompt_File_Manager.json'

  .. tab:: python

    .. code-block:: python

        import requests
        url = "localhost:8989/api/plugin-group-permutations?plugin_manifest=https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json&plugin_manifest=https://assistant-management-data.s3.amazonaws.com/Imprompt_File_Manager.json"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)

  .. tab:: REST

    .. code-block:: sh

        API Endpoint: {{SERVER_ENDPOINT}}/api/plugin-group-permutations?plugin_manifest=https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json&plugin_manifest=https://assistant-management-data.s3.amazonaws.com/Imprompt_File_Manager.json

        Method: GET

        Headers: {
          'x-api-key': 'your-api-key'
          'Content-Type': 'application/json'
        }


Response
============

.. code-block:: json

    [
        {
            "name": "Plugin Group 1",
            "plugins": [
                {
                    "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
                }
            ]
        },
        {
            "name": "Plugin Group 2",
            "plugins": [
                {
                    "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Imprompt_File_Manager.json"
                }
            ]
        },
        {
            "name": "Plugin Group 3",
            "plugins": [
                {
                    "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
                },
                {
                    "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Imprompt_File_Manager.json"
                }
            ]
        }
    ]


