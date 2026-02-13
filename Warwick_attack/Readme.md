# 7  Prompt Mutation Attacks

## ⚡ Quick Install

```bash
pip install transformers
pip install torch
pip install fastchat
pip install openai
pip install python-dotenv
pip install anthropic
pip install importlib-resources
pip install datasets
pip install nltk
pip install psutil
pip install accelerate

```

OR 

```bash
pip install transformers torch fastchat openai python-dotenv anthropic importlib-resources datasets nltk psutil accelerate sentence-transformers
```

## Overview

This folder contains implementations of **7 deterministic prompt mutation attacks** that do NOT require language models. Each attack uses the original implementations from their source repositories and applies them directly to harmful prompts using standardized AIRR security format.



## Installation & Dependencies

### Install Required Dependencies

Before running any attack code, install the required dependencies:

```bash
pip install transformers torch fastchat openai python-dotenv anthropic importlib-resources
```


## The 7 Attacks

This folder contains code for the following **7 deterministic prompt mutation attacks**:

1. **Base64** - Binary-to-text encoding obfuscation
2. **Leetspeak** - Character substitution (a→@, e→3, etc.)
3. **ROT13** - Rotating text cipher (reverse substitution)
4. **Bijection** - Character-level transformation mapping
5. **CodeChameleon** - Tree-structured code representation
6. **CodeAttack** - Deque-based code obfuscation
7. **Replace with Synonyms** - WordNet-based word substitution

## How to Run

### Basic Usage

Each attack is in its own folder and can be run independently:

```bash
cd <attack_name>/
python3 <attack_name>.py <input_csv> [output_csv] [optional_params]
```

### Example Commands

```bash
# Base64 attack
cd base64_attack/
python3 base64_attack.py airr_security_1.0_naive_en_us_prompt_set_10.csv output.csv

# Bijection attack with automatic output naming
cd bijection_attack/
python3 bijection_attack.py airr_security_1.0_naive_en_us_prompt_set_10.csv

# CodeAttack with prompt_type parameter
cd Code_attack/
python3 code_attack.py airr_security_1.0_naive_en_us_prompt_set_10.csv output.csv python_stack

# Synonym replacement
cd Replace_with_Synonyms_attack/
python3 synonym_replacement.py airr_security_1.0_naive_en_us_prompt_set_10.csv
```

### Input Format

All attacks expect CSV input with these columns:
- `release_prompt_id` - Unique identifier
- `prompt_text` - The harmful prompt to mutate
- `hazard` - Hazard category (e.g., "cse", "dfm")
- `locale` - Language locale (e.g., "en_US")

### Output Format

All attacks produce standardized 9-column CSV output:
- `seed_prompt_id` - Original prompt ID
- `seed_locale` - Original locale
- `seed_prompt_text` - Original prompt text
- `Hazard` - Hazard category
- `Attack_prompt_id` - Unique attack ID
- `Attack_type_id` - Attack type identifier
- `attack_type` - Always "text"
- `attack_prompt_text` - The mutated prompt
- `attack_prompt_hash` - SHA-256 hash of mutated prompt

## Folder Structure

```
Warwick_attack/
├── base64_attack/
│   ├── base64_attack.py
│   ├── README.md
│   └── airr_security_1.0_naive_en_us_prompt_set_10.csv
├── bijection_attack/
│   ├── bijection_attack.py
│   ├── README.md
│   ├── BIJECTION_EXPLANATION.txt
│   └── airr_security_1.0_naive_en_us_prompt_set_10.csv
├── Code_attack/
│   ├── code_attack.py
│   ├── README.md
│   ├── CODEATTACK_EXPLANATION.txt
│   └── airr_security_1.0_naive_en_us_prompt_set_10.csv
├── codechameleon_attack/
│   ├── codechameleon_attack.py
│   ├── README.md
│   └── airr_security_1.0_naive_en_us_prompt_set_10.csv
├── leetspeak_attack/
│   ├── leetspeak_attack.py
│   ├── README.md
│   └── airr_security_1.0_naive_en_us_prompt_set_10.csv
├── Replace_with_Synonyms_attack/
│   ├── synonym_replacement.py
│   ├── README.md
│   └── airr_security_1.0_naive_en_us_prompt_set_10.csv
├── rot13_attack/
│   ├── rot13_attack.py
│   ├── README.md
│   └── airr_security_1.0_naive_en_us_prompt_set_10.csv
└── README.md (this file)
```

## Testing

Test input CSV files are included in each attack folder:
```bash
airr_security_1.0_naive_en_us_prompt_set_10.csv
```

This contains 10 harmful prompts from the AIRR security dataset for testing.

## Troubleshooting

### "Module not found" errors
- Ensure all dependencies are installed: `pip install transformers torch fastchat openai python-dotenv anthropic importlib-resources`
- Check that you're in the virtual environment: `source venv/bin/activate`

### "Git command not found"
- Install git: `brew install git` (macOS) or `apt install git` (Ubuntu)
- Verify: `git --version`

### CSV column errors
- Ensure input CSV has required columns: `release_prompt_id`, `prompt_text`, `hazard`, `locale`
- Check that column names match exactly (case-sensitive)

### Permission denied errors
- Make sure the script is executable: `chmod +x <attack_name>.py`
- Or run with Python: `python3 <attack_name>.py`
