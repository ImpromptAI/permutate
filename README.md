# Permutate
![Alt text](https://github.com/LegendaryAI/permutate/blob/main/docs/permutate-logo.png)
## Permutate is an automated testing framework for LLM Plugins. 

### ChatGPT Ignited LLM Plugins
ChatGPT spread like wildfire but it had some limitations, notably, it couldn’t access private data/systems. But this limitation was resolved with the release of OpenAI Plugins. This enabled developers to connect their favorite applications to ChatGPT. Unfortunately, in the rush to release plugins, quality assurance lacked. 

From a software quality perspective, several common problems surfaced:
<ul>
<li>Despite the plugin being “installed” in a user’s environment, the plugin wasn’t consistently activated by the user’s text.</li>
<li>When it was activated, the plugin wasn’t called correctly, leading to undesirable results.</li>
</ul>

Ultimately, plugin developers chose to remove the bulk of their features just to get basic functions to run correctly. 🙁

  
---
  
![Alt text](https://github.com/LegendaryAI/permutate/blob/main/docs/permutate-overview.png) 


---
  
  
### Introducing Permutate
Permutate is an automated testing framework for LLM Plugins. 

Permutate allows development teams to:
<ul>
<li>Define a set of reusable tests for plugins</li>
<li>Describe the tests using a standard, open format</li>
<li>Use open source software (Permutate) to execute the tests</li>
<li>See the results of individual test cases as well as summary statistics</li>
</ul>


#### The Permutation Problem 
When users give prompts (instructions to an LLM via chat, etc.), they use a variety of ways of describing what they want. Each sentence variation might work or fail. The goal is to get as many of them to succeed as possible. 

Some technology (the tool selector) must determine what the intent of the command was (aka, intent detection). Additionally, the command might have extra data like “in the morning” or “once per week”. This natural language needs to be mapped back to an API. The Tool Selector must do more than just ‘find the right tool’, it must map language to an API and call it perfectly. 

So, here we go. Given J variations of sample input text, and K variations of "installed" plugins, we use a tool selector and evaluate the performance:
<ol>
<li>Is the correct plugin selected?</li>
<li>Is the correct API operation selected?</li>
<li>Are the API parameters filled in correctly?</li>
<li>What was the cost to solve?</li>
<li>And, what was the round-trip latency?</li>
</ol>

### Tool Selectors 
To satisfy these concerns, developers will use a Tool Selector service. Here, they pass in the text, and it identifies the correct plugin to use, the right operations, etc. In some cases, they might return the necessary source code to call the API, with all of the parameters filled in. 

To make life simple, we created OpenPlugin. This is optional. This allows plugin service providers to offer their best implementation possible. If an implementation isn’t giving you the accuracy or performance you need, try another. But more importantly, it allows you to test plugins using basic CI/CD principles.  

#### Does this work with OpenAI Plugins and/or Functions?
Yes - for OpenAI Functions. 
For OpenAI Plugins, the answer is "mostly" both Imprompt and LangChain have emulated their approach and via those bindings, you can test the Manifest file approach. 


### Getting started

#### Installation
To install using pip, run:
```sh
pip install permutate
```
You can verify you have permutate installed by running:
```sh
permutate --help
```

#### Credentials
Before you run the application, be sure you have credentials configured.
```sh
export OPENAI_API_KEY=<your key> // if you want to use OpenAI LLM
export COHERE_API_KEY=<your key> // if you wan to use Cohere LLM
export GOOGLE_APPLICATION_CREDENTIALS=<credential_file_path: /usr/app/application_default_credentials.json> // if you want to use Google LLM
```

#### Create your test file
Sample test file: https://raw.githubusercontent.com/LegendaryAI/permutate/main/tests/files/plugin_test.yaml

```commandline
version: 1.0.0
name: klarna_plugin_test
config:
  use_openplugin_library: true
  langchain_tool_selector: http://localhost:8006/api/langchain/run-plugin
  imprompt_tool_selector: http://localhost:8006/api/imprompt/run-plugin
  auto_translate_to_languages:
    - English
    - Spanish
test_plugin:
    manifest_url: https://www.klarna.com/.well-known/ai-plugin.json
plugin_groups:
  - plugin_group:
    name: my_group1
    plugins:
      - plugin:
        manifest_url: https://www.klarna.com/.well-known/ai-plugin.json
  - plugin_group:
    name: my_group2
    plugins:
      - plugin:
        manifest_url: https://www.klarna.com/.well-known/ai-plugin.json
      - plugin:
        manifest_url: https://api.imprompt.ai/plugin/users/2/blogwriter/.well-known/ai-plugin.json
permutations:
  - permutation:
    name: permutation1
    llm:
      provider: OpenAIChat
      model_name: gpt-3.5-turbo
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
  - permutation:
    name: permutation2
    llm:
      provider: OpenAIChat
      model_name: gpt-3.5-turbo
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
test_cases:
  - test_case:
    name: test1
    prompt: Show me 5 T shirts from Klarna
    expected_plugin_used: KlarnaProducts
    expected_api_used: https://www.klarna.com/us/shopping/public/openai/v0/products
    expected_parameters:
      q: t shirt
      size: 5
    expected_response: List of 5 T shirts with URL
  - test_case:
    name: test2
    prompt: Get me 5 oranges
    expected_plugin_used: None
    expected_api_used: None
    expected_parameters:
      num_shirts: None
    expected_response: None
```

#### Run your test file


    Usage: permutation run [TEST_FILE_PATH] [OPTIONS]
    
    Run a permutation batch

    Arguments:
      test_file_path        Plugin test setup file.
                            default: /permutate/workspace/plugin_test.yaml

    Options:
      --help                                   show this help message and exit
      --save-to-html  --no-save-to-html        Save the results of the permutation run to an html file.
                                               default: save-to-html
      --save-to-csv   --no-save-to-csv         Save the results of the permutation run to a csv file.
                                               default: no-save-to-csv
      --output-directory                       Path to the directory where the output files will be saved.
                                               default: /permutate/workspace/output/

***Examples:***

This command will run the tests defined in the plugin_test.yaml file and save the results to a csv file and an html file in the directory pointed by the flag --output-directory.
```sh
permutate run tests/files/plugin_test.yaml --output-directory tests/files/output/ --save-to-csv --save-to-html 
```

This command will run the tests on a sample test file provided in the package and save the results to an html file. This command can be used to see the sample output.

```sh
permutate run
```

#### Docker
```shell
docker run -v /LOCALPATH/plugin_test.yaml:/usr/app/plugin_test.yaml -e "OPENAI_KEY=your-key" -e "COHERE_API_KEY=your-key" -e "GOOGLE_APPLICATION_CREDENTIALS=your-file-path" shrikant14/permutate:latest
```

##### Output
You can save your permutate run output to: 
1. HTML Report:

    You can save your permutation run output to an HTML Report that presents the results of the permutation run in a structured and visually appealing format.

   Sample report: https://raw.githubusercontent.com/LegendaryAI/permutate/main/docs/sample_result.html

   https://raw.githubusercontent.com/LegendaryAI/permutate/main/docs/sample_result_screenshot.png
   ![Alt text](docs/sample_result_screenshot.png?raw=75x75 "Logo")


2. CSV Report.

    You can save your permutation run output to two csv files: one for the permutation run summary and one for the permutation run details.
    
    Sample summary: https://raw.githubusercontent.com/LegendaryAI/permutate/main/docs/sample_result_summary.csv

    Sample details: https://raw.githubusercontent.com/LegendaryAI/permutate/main/docs/sample_result_details.csv

(THIS PROJECT IS NOT RELEASED YET).
More docs coming soon!
