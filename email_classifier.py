import enum
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_community.chat_models import ChatOllama
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI


class Classification(enum.Enum):
    important = "important"
    unimportant = "unimportant"


class EmailClassifierModel(BaseModel):
    """
    Classifies emails as 'important' or 'unimportant' and provides a reason for the classification.
    """
    classification:  Classification = Field(
        ...,
        description="The classification of the email.",
        required=True
    )
    reason: str = Field(
        ...,
        description="The reason for the classification.",
        required=True
    )


system_prompt = """You are an email classifier. Your job is to analyze the subject, content, and 
sender of an email and determine whether the email is 'important' or 'unimportant'. ALWAYS provide a reason for your 
answer. Use the provided examples to guide your classification.

An email is considered 'important' if it requires timely action, is from a 
significant contact, or contains critical information. Examples include emails 
from your work, project updates, urgent requests, or important personal messages.

An email is considered 'unimportant' if it is a promotional message, a routine 
notification, or spam. Examples include advertisements, social media updates, 
newsletters, and generic greetings.

Always respond with either 'important' or 'unimportant' as the classification and the reason for 
your answer."""


class EmailClassifier:
    """
    Email classifier.
    """

    def __init__(self, openai=False):
        if openai:
            self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
        else:
            print("Using Ollama model for email classification.")
            self.llm = OllamaFunctions(model="llama3")

    def classify_email(self, email_details: dict) -> tuple[str, str]:
        """
        Classify an email using the Ollama model.
        :param email_details: Email details.
        :return: Email classification.
        """
        user_prompt = (f"Given an email with sender: {email_details['sender']}, subject: {email_details['subject']}, "
                       f"body: {email_details['body']}\n\n classify the email as 'important' or 'unimportant'.")
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        # json_schema = self._classifier_json_schema()
        structured_output = self.llm.with_structured_output(EmailClassifierModel)
        print("Invoking prompt...")
        response = structured_output.invoke(messages)
        print(response)
        classification = response.get("classification", "")
        reason = response.get("reason", "")
        return classification, reason

    def _create_prompt(self) -> ChatPromptTemplate:
        """
        Create a prompt template for the email classifier.
        :return: Prompt template.
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_prompt,
                ),
                ("user", "{input}"),
            ]
        )
        return prompt

    def _classifier_json_schema(self) -> dict:
        """
        Return the JSON schema of the email classifier.
        :return: JSON schema.
        """
        return {
            "title": "email_classifier",
            "description": "Classifies emails as 'important' or 'unimportant' and provides a reason for the "
                           "classification.",
            "type": "object",
            "properties": {
                "classification": {
                    "type": "string",
                    "enum": ["important", "unimportant"],
                    "description": "The classification of the email. Either 'important' or 'unimportant'."
                },
                "reason": {
                    "type": "string",
                    "description": "The reason for the classification of the email."
                }
            },
            "required": ["classification", "reason"]
        }
