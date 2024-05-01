import argparse

from clickbait_commit_messages import get_provider


def list_available_models() -> list[str]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--provider",
        type=str,
        default="huggingface",
        help="The provider to use for generating the clickbaity message.",
    )
    args = parser.parse_args()

    return get_provider(args.provider).list_available_models()
