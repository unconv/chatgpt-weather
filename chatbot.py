#!/usr/bin/env python3

import openai
import os
import sys
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

# the actual weather function
def get_current_weather(location = None):
    if location is None:
        return "A location must be provided. Please ask the user which location they want the weather for"
    return "The weather is nice and sunny"

# the function defintion for chatgpt
def gpt_functions():
    return [{
        "name": "get_current_weather",
        "description": "Gets the current weather information",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "An optional location for which to get the weather information",
                },
            },
            "required": [],
        },
    }]

# ChatGPT API Function
def send_message(
    message,
    messages
):
    # add user message to message list
    messages.append(message)

    try:
        # send prompt to chatgpt
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=messages,
            functions=gpt_functions(),
            function_call="auto",
        )
    except openai.error.AuthenticationError:
        print("AuthenticationError: Check your API-key")
        sys.exit(1)

    # add response to message list
    messages.append(response["choices"][0]["message"])

    return messages

# MAIN FUNCTION
def run_conversation(prompt, messages = []):
    # add user prompt to chatgpt messages
    messages = send_message({"role": "user", "content": prompt}, messages)

    # get chatgpt response
    message = messages[-1]

    # loop until project is finished
    while True:
        if message.get("function_call"):
            # get function name and arguments
            function_name = message["function_call"]["name"]
            arguments = json.loads(message["function_call"]["arguments"])

            if function_name == "get_current_weather":
                function_response = get_current_weather(**arguments)

                # send function result to chatgpt
                messages = send_message({
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }, messages)
        else:
            # if chatgpt doesn't respond with a function call, ask user for input
            print("ChatGPT: " + message["content"])

            user_message = input("You: ")

            # send user message to chatgpt
            messages = send_message({
                "role": "user",
                "content": user_message,
            }, messages)

        # save last response for the while loop
        message = messages[-1]

# ASK FOR PROMPT
print("Go ahead, ask anything!")
prompt = input("You: ")

# RUN CONVERSATION
run_conversation(prompt)
