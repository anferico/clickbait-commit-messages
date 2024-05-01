# clickbait-commit-messages
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

Make your commit messages extremely catchy.

## Prerequisites
- Hugging Face access token (if using the Hugging Face provider): [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- Groq API token (if using the Groq provider): [https://console.groq.com/keys](https://console.groq.com/keys)

## How to use
This tool is meant to be used in conjunction with [pre-commit](https://pre-commit.com/). In order to use it, you should:
1. Install `clickbait-commit-messages`
    ```
    pip install clickbait-commit-messages
    ```
2. Add the following entry to your `.pre-commit-config.yaml` file:
    ```yaml
    default_install_hook_types: [pre-commit, prepare-commit-msg]
    repos:
    - repo: local
        hooks:
        - id: make-clickbaity
          name: make-clickbaity
          entry: make-clickbaity
          language: python
          stages: [prepare-commit-msg]
          verbose: true
    ```
    Please note a couple of things:
    1. `default_install_hook_types: [pre-commit, prepare-commit-msg]` tells pre-commit to install the `make-clickbaity` git hook at a different stage than the default one (which is `pre-commit`). If you omit this line, `pre-commit` will _not_ install this hook to run during the `prepare-commit-msg` stage (i.e. _after_ the commit is done but before the commit message is confirmed), which is indeed the only stage this hook is meant to run at (that's why we set `stages: [prepare-commit-msg]` by the way)
    2. Rather than specifying the repo URL in the `repo` field, you must put "local". This is because in order to run properly, this hook has to have access to your local environment. In particular, it needs to be able to access the `HF_TOKEN` and/or the `GROQ_API_TOKEN` environment variable (see step 3)
3. Run `pre-commit install` to install the hook
4. Based on which _provider_ (external API service to generate clickbait commit messages) you wish to use, run:

   [Hugging Face](https://huggingface.co/docs/api-inference/index)

    ```
    export HF_TOKEN=hf_**********************************
    ```
   [Groq](https://groq.com/)

    ```
    export GROQ_API_TOKEN=gsk_****************************************************
    ```
    Where obviously you need to replace the values above with your own token. If you'd rather avoid doing this every time, add that line to your `~/.bashrc` (or equivalents if you're using another shell other than Bash)

## Configuration options
The behavior of this hook can be customized using the following configuration options:
- `--provider`: The provider to use for generating clickbait commit messages. Options: [`huggingface`, `groq`]. Defaults to `huggingface`
- `--model-name`: The actual model to use to turn regular commit messages into clickbaity ones. Each provider has its own available models. Defaults to `mistralai/Mixtral-8x7B-Instruct-v0.1`
  - `list-models -p <provider_name>` lists all the available models for a given provider
- `--style`: The style of clickbait to generate. Supported values: `youtube` (akin to a catchy title of a YouTube video), `news` (akin to a clickbaity title of a news article). Defaults to `youtube`
- `--use-emojis`: Use emojis in the clickbaity message

As an example, here's how you would specify a custom configuration:
```yaml
hooks:
- id: make-clickbaity
  name: make-clickbaity
  entry: make-clickbaity
  args: [
    "--provider", "huggingface",
    "--model-name", "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "--style", "news",
    "--use-emojis"
  ]
  language: python
  stages: [prepare-commit-msg]
  verbose: true
```

## Things to keep in mind
### For the Hugging Face provider
1. Some models, such as `mistralai/Mixtral-8x7B-Instruct-v0.1`, are _gated_, meaning that you need to explicitly request access to them before you can use them via the API. To do that, visit the home page of the model in Hugging Face and follow the instructions to request access to it

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

### For the Groq provider
1. The API server returns empty responses sometimes, in which case the commit messages are left unchanged. I'm not sure why this happens, but it might be due to the high volume of requests sent to the Groq API. For this reason, if you're looking for a more reliable provider, go for Hugging Face
