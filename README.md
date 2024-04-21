# clickbait-commit-messages
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

Make your commit messages extremely catchy.

## How to use
This tool is meant to be used in conjunction with [pre-commit](https://pre-commit.com/). In order to use it, you should:
1. Install `clickbait-commit-messages`: `pip install clickbait-commit-messages`
2. Add the following entry to your `.pre-commit-config.yaml` file:
    ```yaml
    default_install_hook_types: [pre-commit, prepare-commit-msg]
    repos:
    - repo: local
        hooks:
        - id: make-clickbaity
          entry: make-clickbaity
    ```
    Please note a couple of things:
    1. `default_install_hook_types: [pre-commit, prepare-commit-msg]` tells pre-commit to install the `make-clickbaity` git hook at a different stage than the default one (which is `pre-commit`). If you omit this line, `pre-commit` will not install this hook correctly since it's meant to run during the `prepare-commit-msg` stage (i.e. _after_ the commit is done but before the commit message is confirmed)
    2. Rather than specifying the repo URL in the `repo` field, you must put "local". This is because in order to run properly, this hook has to have access to your local environment. In particular, it needs to be able to access the `HF_TOKEN` environment variable (see step 3)
3. Run `export HF_TOKEN=hf_**********************************` (replace with your Hugging Face access token). This is needed as the hook needs to call the Hugging Face API to generate clickbait commit messages. If you'd rather avoid doing this every time, add that line to your `~/.bashrc` (or equivalents for other shells)

## Configuration options
The behavior of this hook can be customized using the following configuration options:
- `--model-name`: The Hugging Face model to use for generating the clickbaity message. Defaults to `mistralai/Mixtral-8x7B-Instruct-v0.1`
- `--style`: The style of clickbait to generate. Supported values: `youtube` (akin to a catchy title of a YouTube video), `news` (akin to a clickbaity title of a news article). Defaults to `news`
- `--template`: The template to use for the chat prompt. Different models may require different chat templates. For example, Mistral/Mixtral models require this template: `<s>[INST]{prompt}[/INST]`. Defaults to `None` (see `--template-style`)

    **NOTE**: it is important that in the chat template you pass here, the actual prompt is abstracted away with the literal string `{prompt}` (as shown above)
- `--template-style`: The style of template to use for the chat prompt, selected among a pre-defined set. Supported values: `mistral`. This argument is meant to be used in a mutually exclusive way with `--template`, meaning you should pass one or the other _but not both_. Defaults to `mistral`, which corresponds to the chat template exemplified above
- `--use-emojis`: Use emojis in the clickbaity message

As an example, here's how you would specify a custom configuration:
```yaml
hooks:
- id: make-clickbaity
  entry: make-clickbaity
  args: [
    "--model-name", "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "--style", "news",
    "--template-style", "mistral",
    "--use-emojis"
  ]
```

## Things to keep in mind
1. Some Hugging Face models, such as `mistralai/Mixtral-8x7B-Instruct-v0.1`, are _gated_, meaning that you need to explicitly request access to them before you can use them via the API. To do that, visit the home page of the model in Hugging Face and follow the instructions to request access to it

2. Some models, such as `meta-llama/Meta-Llama-3-8B-Instruct`, may not be usable on the free tier of the API. When trying to use them to generate a clickbait commit message, you might get an **HTTP 403** error along the lines of:
    ```json
    {"error":"The model meta-llama/Meta-Llama-3-8B-Instruct is too large to be loaded automatically (16GB > 10GB). Please use Spaces (https://huggingface.co/spaces) or Inference Endpoints (https://huggingface.co/inference-endpoints)."}
    ```
    In order to probe whether a model will be usable or not, you can shoot a cURL request like the following and check the response (replace `${MODEL_NAME}` and `${API_TOKEN}` appropriately):
    ```curl
    curl https://api-inference.huggingface.co/models/${MODEL_NAME} \
        -X POST \
        -d '{"inputs": "Some dummy prompt, the format and content are not important"}' \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${API_TOKEN}"
    ```
    If you receive an error message like the one showed above, then it means you can't use that model on your current API tier. Otherwise, you're good to go 👍
