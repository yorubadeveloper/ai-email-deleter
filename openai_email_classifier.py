import os
import json

import openai

# System prompt
system_prompt = """
You are an email classifier. Your job is to analyze the subject, content, and sender of an email and determine whether 
the email is 'important' or 'unimportant'. Use the provided examples to guide your classification.

An email is considered 'important' if it requires timely action, is from a significant contact, or contains critical 
information. Examples include emails from your boss, project updates, urgent requests, or important personal messages.

An email is considered 'unimportant' if it is a promotional message, a routine notification, or spam. Examples include 
advertisements, social media updates, newsletters, and generic greetings.

Always respond with either 'important' or 'unimportant'.
"""

# Function definition
tools = [
    {
        "type": "function",
        "function": {
            "name": "classify_email",
            "description": "Classifies an email as either 'important' or 'unimportant'",
            "parameters": {
                "type": "object",
                "properties": {
                    "classification": {
                        "type": "string",
                        "enum": ["important", "unimportant"],
                        "description": "The classification of the email"
                    }
                },
                "required": ["classification"]
            }
        }
    }
]


def classify_email(email_details: dict) -> str:
    """
    Classify an email as 'important' or 'unimportant' based on its subject, content, and sender.
    :param email_details: Dictionary containing the email details (subject, content, sender).
    :return: The classification of the email.
    """
    # Implement email classification logic here
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",
             "content": f"Subject: {email_details['subject']}\nContent: {email_details['body']}\nSender: {email_details['sender']}"}
        ],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "classify_email"}}
    )

    classification_message = response.choices[0].message
    args = classification_message.tool_calls[0].function.arguments
    resp = json.loads(args, strict=False)
    classification = resp.get("classification", "")
    return classification
