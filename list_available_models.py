from clickbait_commit_messages import get_provider


def list_available_models(provider_name: str = "huggingface") -> list[str]:
    return get_provider(provider_name).list_available_models()
