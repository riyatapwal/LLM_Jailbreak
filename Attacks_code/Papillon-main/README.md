# Papillon Attack

## Prerequisites

- Python 3.10+
- PyTorch (tested with 2.1.2+cu12.1)

## Installation

Install required dependencies:

```bash
pip install "fschat[model_worker,webui]"
pip install vllm 
pip install openai                # for openai LLM
pip install termcolor
pip install openpyxl
pip install google-generativeai   # for google PALM-2
pip install anthropic              # for anthropic
```

## Model Setup

Download the model to `./roberta`:

```bash
bash: https://huggingface.co/hubert233/GPTFuzz ./Roberta
```

## Configuration

Configure API credentials in `Judge/language_models.py` where the client is instantiated.

Example (line 106 in `./Judge/language_models.py`):

```python
client = OpenAI(base_url="[your proxy url(if use)]", api_key="your api key", timeout = self.API_TIMEOUT)
```

## How to Run

The Papillon attack is executed via the `run.py` file.

### Quick Start

Run a simple experiment using OpenAI model as the target:

```bash
python run.py --openai_key YOUR_OPENAI_KEY --model_path gpt-3.5-turbo --target_model gpt-3.5-turbo
```

**Note**: Adjust flags as needed for your environment and target model.
