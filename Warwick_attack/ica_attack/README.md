# ICA Attack (In-Context Attacks - EasyJailbreak)

## Overview

This attack applies In-Context Attack (ICA) mutation to prompts. ICA is a technique that uses few-shot in-context examples to guide an AI model to generate harmful content by demonstrating patterns with similar requests and responses.

The script uses **exact hardcoded demonstrations from EasyJailbreak's seed_template.json**, ensuring alignment with the official framework's ICA implementation. These demonstrations are pre-defined harmful Q&A pairs that establish behavioral patterns.

## Prerequisites

- Python 3.6+
- transformers (required for EasyJailbreak)
- torch (required for EasyJailbreak)
- Virtual environment (recommended)

### Installation

**Step 1: Create and activate a virtual environment (recommended)**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Step 2: Install required packages**

```bash
pip install transformers torch fastchat openai python-dotenv anthropic importlib-resources datasets nltk psutil accelerate
```

Or if `pip` doesn't work, try:
```bash
pip3 install transformers torch fastchat openai python-dotenv anthropic importlib-resources datasets nltk psutil accelerate
```

## How to Run

### Option 1: Using Virtual Environment (Recommended)

```bash
# Activate virtual environment first
source venv/bin/activate

# Then run the script
python ica_attack.py <input_csv_path> [output_csv_path] [num_demos]
```

### Option 2: Using Python Directly from Virtual Environment

```bash
/path/to/venv/bin/python ica_attack.py <input_csv_path> [output_csv_path] [num_demos]
```

## Usage Examples

### Basic Usage (Default: 5 demonstrations)
```bash
python ica_attack.py input_prompts.csv output_mutated.csv
```

### Custom Number of In-Context Examples
```bash
python ica_attack.py input_prompts.csv output_mutated.csv 7
```

### Using Full Path
```bash
python ica_attack.py /path/to/input.csv /path/to/output.csv 10
```

## Input CSV Format

The input CSV must contain the following columns:
- `release_prompt_id`: Unique prompt identifier
- `prompt_text`: The harmful prompt to be mutated
- `hazard`: Hazard category (e.g., "cse", "violence", etc.)
- `locale`: Language/region code (e.g., "en_US")

## Output CSV Format

The output CSV contains:
- `seed_prompt_id`: Original prompt ID
- `seed_locale`: Original locale
- `seed_prompt_text`: Original harmful prompt
- `Hazard`: Hazard category
- `Attack_prompt_id`: Unique ID for the mutated prompt
- `Attack_type_id`: Type of attack (always "ica")
- `attack_type`: Content type (always "text")
- `attack_prompt_text`: The ICA-mutated prompt with in-context examples
- `attack_prompt_hash`: SHA-256 hash of the mutated prompt

## Customization Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `num_demos` | 5 | Number of in-context demonstrations to include (max 5, sourced from EasyJailbreak's seed templates) |

## Notes

- The script uses **exact hardcoded demonstrations from EasyJailbreak's seed_template.json** (5 Q&A pairs)
- These demonstrations cover: suicide instructions, bomb-making, fake news, airport security evasion, and test cheating
- Available demonstrations limit `num_demos` to maximum 5 (requesting more will default to available count)
- SHA-256 hashing ensures unique identification of each mutated prompt
- The attack preserves the original prompt text while creating a jailbreak variant
- More demonstrations can improve attack effectiveness but increase prompt length

