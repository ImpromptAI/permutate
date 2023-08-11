Introduction
===============


Permutate is an automated testing framework for LLM Plugins.

Permutate allows development teams to:

+ Define a set of reusable tests for plugins
+ Describe the tests using a standard, open format
+ Use open source software (Permutate) to execute the tests
+ See the results of individual test cases as well as summary statistics


Architecture
==============

.. image:: /_images/permutate-overview.png
   :alt: Permutate Suite
   :align: center


The Permutation Problem
==========================

When users give prompts (instructions to an LLM via chat, etc.), they use a variety of ways of describing what they want. Each sentence variation might work or fail. The goal is to get as many of them to succeed as possible.

Some technology (the tool selector) must determine what the intent of the command was (aka, intent detection). Additionally, the command might have extra data like “in the morning” or “once per week”. This natural language needs to be mapped back to an API. The Tool Selector must do more than just ‘find the right tool’, it must map language to an API and call it perfectly.

So, here we go. Given J variations of sample input text, and K variations of "installed" plugins, we use a tool selector and evaluate the performance:

1. Is the correct plugin selected?
2. Is the correct API operation selected?
3. Are the API parameters filled in correctly?
4. What was the cost to solve?
5. And, what was the round-trip latency?


Tool Selectors
=================
To satisfy these concerns, developers will use a Tool Selector service. Here, they pass in the text, and it identifies the correct plugin to use, the right operations, etc. In some cases, they might return the necessary source code to call the API, with all of the parameters filled in.

To make life simple, we created OpenPlugin. This is optional. This allows plugin service providers to offer their best implementation possible. If an implementation isn’t giving you the accuracy or performance you need, try another. But more importantly, it allows you to test plugins using basic CI/CD principles.

**Does this work with OpenAI Plugins and/or Functions?**

Yes - for OpenAI Functions. For OpenAI Plugins, the answer is "mostly" both Imprompt and LangChain have emulated their approach and via those bindings, you can test the Manifest file approach.
