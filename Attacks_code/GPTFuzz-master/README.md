# GPTFuzz Attack

## Environment Setup

Create a conda environment with Python 3.8:

```bash
conda create -n gptfuzz python==3.8
conda activate gptfuzz
```

## Installation

### PyTorch

Install the PyTorch version that matches your CUDA version:

```bash
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
```

### FastChat

Install the FastChat package:

```bash
pip3 install "fschat[model_worker,webui]"
```

Or install from source:

```bash
git clone https://github.com/lm-sys/FastChat.git
cd FastChat
pip3 install --upgrade pip  # enable PEP 660 support
pip3 install -e ".[model_worker,webui]"
```

### vLLM

Install vLLM (from pip or source):

```bash
pip install vllm
```

Or install from source code (recommended for CUDA 12):

```bash
git clone https://github.com/vllm-project/vllm.git
cd vllm
python setup.py develop
```

### Additional Dependencies

Install the following packages:

```bash
pip install openai                # for openai LLM
pip install termcolor
pip install openpyxl
pip install google-generativeai   # for google PALM-2
pip install anthropic              # for anthropic
```

## Model Testing

After installation, you should be able to use HuggingFace and vLLM inference. Here's a quick test example:

```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '1,2'  # specify which GPU(s) to use

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from vllm import LLM, SamplingParams

model_path = "meta-llama/Llama-2-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side='left', use_fast=False)
tokenizer.pad_token = tokenizer.eos_token

sampling_params = SamplingParams(temperature=0.0, max_tokens=512)
model_vllm = LLM(model=model_path, gpu_memory_utilization=0.95)
model_hf = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, device_map='cuda:1').eval()

LLAMA2_PROMPT = {
    "description": "Llama 2 chat one shot prompt",
    "prompt": '''[INST] <<SYS>>
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
<</SYS>>

{instruction} [/INST] '''
}

prompt = ["What is the capital of France?", "What is the capital of Germany?", "What is the capital of Italy?"]

llama_input = [LLAMA2_PROMPT['prompt'].format(instruction=p) for p in prompt]

# vLLM inference
vllm_output = model_vllm.generate(llama_input, sampling_params=sampling_params)
for output in vllm_output:
    generated_text = output.outputs[0].text
    print(f"Generated text by vllm: {generated_text!r}")

# HuggingFace inference
input_ids = tokenizer(llama_input, padding=True, return_tensors="pt")
input_ids['input_ids'] = input_ids['input_ids'].to('cuda:1')
input_ids['attention_mask'] = input_ids['attention_mask'].to('cuda:1')
num_input_tokens = input_ids['input_ids'].shape[1]
outputs = model_hf.generate(input_ids['input_ids'], attention_mask=input_ids['attention_mask'].half(),
                         max_new_tokens=512, do_sample=False, pad_token_id=tokenizer.pad_token_id)
generation = tokenizer.batch_decode(outputs[:, num_input_tokens:], skip_special_tokens=True)
print(generation)
```

## How to Run

Run the GPTFuzz attack using the `gptfuzz.py` file:

```bash
python gptfuzz.py
```
