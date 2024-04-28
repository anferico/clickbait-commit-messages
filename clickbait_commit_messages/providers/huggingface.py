import os
from functools import lru_cache

from huggingface_hub import InferenceClient

from clickbait_commit_messages.providers import (
    BaseProvider,
    ProviderInitializationError,
    register_provider,
)


@register_provider("huggingface")
class HuggingFaceProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__()
        if "HF_TOKEN" not in os.environ:
            raise ProviderInitializationError(
                "Must set the HF_TOKEN environment variable to use the "
                "'huggingface' provider."
            )
        self.client = InferenceClient(token=os.environ["HF_TOKEN"])

    @lru_cache(maxsize=1)
    def list_available_models(self) -> list[str]:
        return self.client.list_deployed_models()["text-generation"]

    @lru_cache(maxsize=1)
    def do_chat_completion(self, prompt: str, model_name: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        return self.client.chat_completion(
            messages, model=model_name, max_tokens=100
        )
