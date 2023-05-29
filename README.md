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
(THIS PROJECT IS NOT RELEASED YET).
More docs coming soon!
