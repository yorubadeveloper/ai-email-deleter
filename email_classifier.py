import re

from langchain_community.llms import Ollama
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate


llm = Ollama(model="llama3", system="You are an email classifier. Your job is to analyze the subject, content, and "
                                    "sender of an email and determine whether the email is 'important' or "
                                    "'unimportant'. Use the provided examples to guide your classification.\n\n"
                                    "An email is considered 'important' if it requires timely action, is from a "
                                    "significant contact, or contains critical information. Examples include emails "
                                    "from your boss, project updates, urgent requests, or important personal messages.\n\n"
                                    "An email is considered 'unimportant' if it is a promotional message, a routine "
                                    "notification, or spam. Examples include advertisements, social media updates, "
                                    "newsletters, and generic greetings.\n\n"
                                    "Always respond with either 'important' or 'unimportant'.")


def create_prompt_template() -> FewShotPromptTemplate:
    """
    Create a prompt template for the email classifier.
    :return: Prompt template.
    """

    examples = [
        {"input": "Given an email with sender: bank@security.com, subject: Your monthly statement is ready, body: This "
                  "email contains your bank statement for the month of May. Please review the attached document for "
                  "details.\n\n"
                  "classify the email as 'Important' or 'Unimportant'.",
         "output": "Important, because it contains bank information."},

        {"input": "Given an email with sender: promotions@retailstore.com, subject: Huge savings this weekend!, body: "
                  "Get 50% off all summer clothing this weekend only! Shop now and save big!\n\n"
                  "classify the email as 'Important' or 'Unimportant'.",
         "output": "Unimportant, because it is a promotional message."},
    ]
    example_template = """
    user: {input}
    ai: {output}
    """
    suffix = """
    user: {input}
    ai: """
    example_prompt = PromptTemplate(
        input_variables=["input", "output"],
        template=example_template
    )
    few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        input_variables=["input"],
        suffix=suffix
    )
    return few_shot_prompt


class EmailOutputParser(BaseOutputParser):
    """Custom output parser to classify email importance."""

    def parse(self, output):
        output = output.strip().lower()

        pattern_important = r'\bimportant\b'
        pattern_unimportant = r'\bunimportant\b'

        match_important = re.search(pattern_important, output)
        match_unimportant = re.search(pattern_unimportant, output)

        if match_unimportant:
            return 'unimportant'
        elif match_important:
            return 'important'
        else:
            return 'unknown'


def classify_email(email_details: dict) -> str:
    """
    Classify an email using the Ollama model.
    :param email_details: Email details.
    :return: Email classification.
    """
    user_prompt = (f"Given an email with sender: {email_details['sender']}, subject: {email_details['subject']}, "
                   f"body: {email_details['body']}\n\n classify the email as 'Important' or 'Unimportant'.")
    prompt_template = create_prompt_template()
    chain = prompt_template | llm | EmailOutputParser()
    parsed_response = chain.invoke({"input": user_prompt})
    return parsed_response
