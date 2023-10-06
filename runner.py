{
    "version": "1.0.0",
    "config": {
        "auto_translate_to_languages": [],
        "openai_api_key": "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",
    },
    "test_plugin": {
        "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
    },
    "permutation_config": {
        "strategies": ["OAI Functions"],
        "llms": [
            {
                "provider": "OpenAI",
                "model": "gpt-4",
                "temperature": 0,
                "max_tokens": 1024,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "n": 1,
                "best_of": 1,
            }
        ],
    },
    "test_cases": [
        {
            "id": "2c0f215b-dbd9-4524-8c38-9599d348a3e1",
            "prompt": "Show me some T Shirts.",
            "expected_plugin_used": "Klarna Shopping",
            "expected_api_used": "/public/openai/v0/products",
            "expected_method": "get",
            "expected_parameters": {
                "countryCode": "US",
                "q": "T Shirts",
                "size": 10,
                "min_price": "",
                "max_price": "",
            },
        }
    ],
    "name": "Klarna Shopping Permutation Test",
    "operations": ["get /public/openai/v0/products"],
}
