from __future__ import annotations

import argparse
from pathlib import Path

from clickbait_commit_messages import get_provider
from clickbait_commit_messages.providers import ProviderInitializationError


def make_clickbaity(
    commit_message,
    /,
    provider_name="huggingface",
    model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
    style="youtube",
    use_emojis=True,
) -> str:
    prompt = get_prompt(commit_message, style, use_emojis)
    provider = get_provider(provider_name)
    clickbait_commit_message = provider.do_chat_completion(prompt, model_name)
    return clickbait_commit_message.strip()


def get_prompt(
    commit_message: str, style: str = "youtube", use_emojis: bool = False
):
    style_description = get_style_description(style)
    emoji_disclaimer = (
        "Use emojis to make it sound even more catchy. " if use_emojis else ""
    )
    prompt = (
        "Rewrite the following git commit message as if it was "
        f"{style_description}. {emoji_disclaimer}Do not add notes or "
        "additional content before or after generating the clickbaity commit "
        "message. Do not make it longer than one line. Here is the original "
        f"commit message: {commit_message}"
    )
    return prompt


def get_style_description(style: str = "youtube"):
    style2description = {
        "youtube": "a clickbaity title of a YouTube video",
        "news": "a clickbaity title of a news article",
    }
    return style2description.get(style, "youtube")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "commit_message_file",
        type=Path,
        help="File containing the commit message to make clickbaity.",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="huggingface",
        help=(
            "The provider to use for generating the clickbaity message. "
            "Supported providers: ['huggingface', 'groq']"
        ),
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="mistralai/Mixtral-8x7B-Instruct-v0.1",
        help="The model to use for generating the clickbaity message.",
    )
    parser.add_argument(
        "--style",
        type=str,
        default="youtube",
        help=(
            "The style of clickbait to generate. Supported styles: "
            "['youtube', 'news']"
        ),
    )
    parser.add_argument(
        "--use-emojis",
        action="store_true",
        help="Whether to use emojis in the clickbaity message.",
    )
    args = parser.parse_args()

    original_commit_message = args.commit_message_file.read_text().strip()
    try:
        clickbaity_commit_message = make_clickbaity(
            original_commit_message,
            provider_name=args.provider,
            model_name=args.model_name,
            style=args.style,
            use_emojis=args.use_emojis,
        )
        args.commit_message_file.write_text(clickbaity_commit_message)
    except ProviderInitializationError:
        print(
            "Could not initialize the provider. Make sure the necessary "
            "environment variables are set. Leaving the commit message as is."
        )


if __name__ == "__main__":
    main()
