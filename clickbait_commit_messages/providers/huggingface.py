import os
from functools import lru_cache
from typing import Any

import huggingface_hub
from requests.exceptions import HTTPError

from clickbait_commit_messages.providers import (
    BaseProvider,
    ProviderInitializationError,
    register_provider,
)


def hf_api_call(default_return_value: Any):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except (huggingface_hub.InferenceTimeoutError, HTTPError) as e:
                if isinstance(e, huggingface_hub.InferenceTimeoutError):
                    print("Hugging Face: model unavailable/request timed out.")
                if isinstance(e, HTTPError):
                    print("Hugging Face: non-200 status code received.")
                return default_return_value

        return wrapper

    return decorator


@register_provider("huggingface")
class HuggingFaceProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__()
        if "HF_TOKEN" not in os.environ:
            raise ProviderInitializationError(
                "Must set the HF_TOKEN environment variable to use the "
                "'huggingface' provider."
            )
        self.client = huggingface_hub.InferenceClient(
            token=os.environ["HF_TOKEN"], timeout=3.0
        )

    @hf_api_call(default_return_value=[])
    @lru_cache
    def list_available_models(self) -> list[str]:
        return self.client.list_deployed_models()["text-generation"]

    @hf_api_call(default_return_value="")
    @lru_cache
    def do_chat_completion(self, prompt: str, model_name: str) -> str:
        chat_completion = self.client.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model_name,
            max_tokens=100,
            stop=["\n"],
        )
        return chat_completion.choices[0].message.content
