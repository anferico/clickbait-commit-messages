import os
from functools import lru_cache
from typing import Any

import groq

from clickbait_commit_messages.providers import (
    BaseProvider,
    ProviderInitializationError,
    register_provider,
)


def groq_api_call(default_return_value: Any):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except (
                groq.APIConnectionError,
                groq.RateLimitError,
                groq.APIStatusError,
            ) as e:
                if isinstance(e, groq.APIConnectionError):
                    print("Groq: server could not be reached.")
                if isinstance(e, groq.RateLimitError):
                    print("Groq: rate limit exceeded.")
                if isinstance(e, groq.APIStatusError):
                    print("Groq: non-200 status code received.")
                return default_return_value

        return wrapper

    return decorator


@register_provider("groq")
class GroqProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__()
        if "GROQ_API_KEY" not in os.environ:
            raise ProviderInitializationError(
                "Must set the GROQ_API_KEY environment variable to use the "
                "'groq' provider."
            )
        self.client = groq.Groq(
            api_key=os.environ["GROQ_API_KEY"], timeout=3.0, max_retries=2
        )

    @groq_api_call(default_return_value=[])
    @lru_cache
    def list_available_models(self) -> list[str]:
        return [
            model.id
            for model in self.client.models.list().data
            if model.active
        ]

    @groq_api_call(default_return_value="")
    @lru_cache
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
