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

#### Is this just for OpenAI?
No. OpenAI hasn’t (yet) made their tool selector service available to the public. We encourage all vendors to make their tool selector service available. This allows for headless automation testing, and without it, we can anticipate poor plugin quality. 

Until OpenAI makes their Tool Selector service available to the public, you have two options:
<ol>
<li>Manual Testing</li>
<li>UI Testing (e.g., Selenium Hell).</li>
</ol>

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
Before you can deploy an application, be sure you have credentials configured.
```sh

```

#### Create your test file
TODO



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

##### Output
You can save your permutate run output to: 
1. HTML Report:

    You can save your permutation run output to an HTML Report that presents the results of the permutation run in a structured and visually appealing format.

    Report sample: https://legendaryai.github.io/permutate/

![Alt text](docs/sample_result_screenshot.png?raw=75x75 "Logo")


2. CSV Report.

    You can save your permutation run output to two csv files: one for the permutation run summary and one for the permutation run details.
    
    Summary sample: https://legendaryai.github.io/permutate/

    Details sample: https://legendaryai.github.io/permutate/

(THIS PROJECT IS NOT RELEASED YET).
More docs coming soon!
