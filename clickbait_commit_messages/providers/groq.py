import os
from functools import lru_cache

from groq import Groq

from clickbait_commit_messages.providers import (
    BaseProvider,
    ProviderInitializationError,
    register_provider,
)


@register_provider("groq")
class GroqProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__()
        if "GROQ_API_KEY" not in os.environ:
            raise ProviderInitializationError(
                "Must set the GROQ_API_KEY environment variable to use the "
                "'groq' provider."
            )
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])

    @lru_cache(maxsize=1)
    def list_available_models(self) -> list[str]:
        # TODO: filter out non-active models
        return [model.id for model in self.client.models.list().data]

    @lru_cache(maxsize=1)
    def do_chat_completion(self, prompt: str, model_name: str) -> str:
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model_name,
        )
        return chat_completion.choices[0].message.content
