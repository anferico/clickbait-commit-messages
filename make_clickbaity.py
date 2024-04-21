from __future__ import annotations

import argparse
import os
from pathlib import Path

import requests

API_URL = "https://api-inference.huggingface.co/models/{model_name}"


def make_clickbaity(
    commit_message,
    /,
    model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
    style="youtube",
    template=None,
    template_style="mistral",
    use_emojis=True,
) -> str:
    hf_access_token = os.getenv("HF_TOKEN")
    if hf_access_token is None:
        print(
            "The HF_TOKEN environment variable is not set. Leaving the commit "
            "message unchanged."
        )
        return commit_message

    headers = {
        "Authorization": f"Bearer {hf_access_token}",
        "Content-Type": "application/json",
    }
    prompt = get_prompt(
        commit_message, style, template, template_style, use_emojis
    )
    response = requests.post(
        API_URL.format(model_name=model_name),
        headers=headers,
        json={"inputs": prompt},
        timeout=5,
    )
    response.raise_for_status()

    generated_text = response.json()[0]["generated_text"]
    if generated_text.startswith(prompt):
        generated_text = generated_text[len(prompt) :]
    return generated_text.strip()


def get_prompt(
    commit_message: str,
    style: str = "youtube",
    template: str | None = None,
    template_style: str | None = "mistral",
    use_emojis: bool = False,
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
    return apply_chat_template(prompt, template, template_style)


def get_style_description(style: str = "youtube"):
    style2description = {
        "youtube": "a clickbaity title of a YouTube video",
        "news": "a clickbaity title of a news article",
    }
    return style2description.get(style, "youtube")


def apply_chat_template(
    prompt: str,
    template: str | None = None,
    template_style: str | None = "mistral",
):
    if bool(template) == bool(template_style):
        raise ValueError(
            "You must provide exactly one of template or template_style."
        )
    if template_style is not None:
        template = get_chat_template(template_style)

    return template.format(prompt=prompt)


def get_chat_template(style: str = "mistral"):
    style2template = {
        "mistral": "<s>[INST]{prompt}[/INST]",
    }
    return style2template.get(style, "mistral")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "commit_message_file",
        type=Path,
        help="File containing the commit message to make clickbaity.",
    )
    parser.add_argument(
        "staged_files",
        type=Path,
        nargs="*",
        help=(
            "Files that are staged for commit. This is a placeholder "
            "argument to ignore the staged files."
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
        help="The style of clickbait to generate.",
    )
    prompt_template_group = parser.add_mutually_exclusive_group(required=True)
    prompt_template_group.add_argument(
        "--template",
        type=str,
        default=None,
        help="The template to use for the chat prompt.",
    )
    prompt_template_group.add_argument(
        "--template-style",
        type=str,
        default="mistral",
        help="The style of template to use for the chat prompt.",
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
            model_name=args.model_name,
            style=args.style,
            template=args.template,
            template_style=args.template_style,
            use_emojis=args.use_emojis,
        )
        args.commit_message_file.write_text(clickbaity_commit_message)
    except requests.exceptions.HTTPError as e:
        print(
            f"make-clickbaity: HTTP error {e.response.status_code}. Leaving "
            "the commit message unchanged."
        )


if __name__ == "__main__":
    main()
