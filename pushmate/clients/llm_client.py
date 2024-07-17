from enum import Enum
from openai import OpenAI

from pushmate.commands.config import Config
from pushmate.utils.messages import print_error


class LLMProvider(Enum):
    OPEN_AI = "openai"


class LLMClient:
    """
    Client to interact with an LLM, regardless of provider
    """

    def __init__(self):
        self.config = Config()
        self.config.get_option("provider")
        self.provider = self.config.get_option("provider")
        self.status = True
        if not self.provider:
            print_error(
                "No provider set. Use [italic]pushmate config --provider[/italic] to set a provider."
            )
            self.status = False
        self.model = ""

    def prompt(self, prompt):
        """
        Generate text based on a prompt
        """
        if not self.status:
            return ""
        try:
            response = ""
            match self.provider:
                case LLMProvider.OPEN_AI.value:
                    self.model = "gpt-4o"
                    response = self.openai_prompt(prompt)
                case _:
                    raise ValueError(f"Provider not supported")

            if response == "":
                print_error("No response from LLM.")

            return response
        except Exception as e:
            if "rate_limit_exceeded" in str(e):
                print_error("LLM rate limit exceeded. Please try again later.")
            else:
                print_error()
            return ""

    def openai_prompt(self, prompt: list[dict[str, str]]):
        """
        Generate text based on a prompt using OpenAI
        """
        api_key = self.config.get_option("openai")
        if not api_key:
            print_error("OpenAI API key not set.")
            return ""

        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(model=self.model, messages=prompt)
        if not completion:
            return ""

        return completion.choices[0].message.content
