# Welcome to the Custom Prompt Mutation Repository

## Overview

This repository contains implementations of **22 prompt mutation attack techniques**.

**Attack Classification:**
- **7 attacks (NO LLM required)**: Use deterministic mutations from original repositories
- **15 attacks (LLM required)**: Need language model APIs or local model downloads

The code implementations are based on **original research repositories** and academic papers. 


## Attack Classification

### 7 Attacks WITHOUT LLM Requirements (Deterministic)
These attacks use exact implementations from original repositories - **no LLM or API keys needed**:

1. **Base64** - Binary-to-text encoding obfuscation
2. **Leetspeak** - Character substitution (a→@, e→3, etc.)
3. **ROT13** - Rotating text cipher (reverse substitution)
4. **Bijection** - Character-level transformation mapping
5. **CodeChameleon** - Tree-structured code representation
6. **CodeAttack** - Deque-based code obfuscation
7. **Replace with Synonyms** - WordNet-based word substitution

**Source**: These use original implementations from:
- EasyJailbreak repository
- haizelabs/bijection-learning
- AI45Lab/CodeAttack

All bridge scripts **auto-clone** the original repositories and run them directly.

### 15 Attacks WITH LLM Requirements
These attacks require language models to generate adversarial prompts:

AutoDAN-Turbo, AutoDAN-GA, Persona, Semantic Shift, Inception, PAIR, TAP, DSN, Papillon, GPTFuzz, CatAttack, Emoji, ICA, and others.

**For LLM-based attacks:**
- **API-based attacks**: Provide templates with API key configuration
- **Model-based attacks**: Require downloading models (LLaMA, others) and local execution
- Refer to original repositories or modify our templates based on your setup

## Installation & Setup

### Step 1: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies
To run the code, install the following required packages:

```bash
pip install transformers torch fastchat openai
```

**Required Dependencies:**
- **transformers** - For Hugging Face model support
- **torch** - PyTorch deep learning framework
- **fastchat** - For conversation templates
- **openai** - For OpenAI API support

These dependencies are needed for the attack implementations and model integrations.

## How to Run

### For Deterministic Attacks (No LLM Required)

All 7 non-LLM attacks use **bridge scripts** that automatically clone and run the original implementations:

```bash
cd Attacks_code/<attack_name>/
python3 <attack>_bridge.py /path/to/your_input.csv
```

**Examples**:
```bash
# Base64 attack
cd Attacks_code/base64_attack/
python3 base64_bridge.py /path/to/Original_prompts.csv

# Leetspeak attack
cd Attacks_code/leetspeak_attack/
python3 leetspeak_bridge.py /path/to/Original_prompts.csv

# ROT13 attack
cd Attacks_code/rot13_attack/
python3 rot13_bridge.py /path/to/Original_prompts.csv
```

**Output**: Creates `Original_prompts_<attack>_mutated.csv` in the same directory as input file

**What the bridge does:**
1. Checks if original repository is cached locally
2. Auto-clones from GitHub if not present
3. Imports and runs the original attack implementation
4. Falls back to basic Python implementation if import fails
5. Outputs standardized CSV format

### For LLM-Based Attacks (LLM Required)

Attacks requiring language models have different execution patterns. **For specific instructions, refer to the README.md file in each attack folder.**

**General approach for LLM attacks:**
- **API-based**: Edit API key configuration in the code, then run
- **Model-based**: Download required models, configure paths, then run
- See individual attack README for detailed setup

### For Detailed Attack-Specific Instructions

Each attack folder contains:
- **README_BRIDGE.md** (for deterministic attacks) - Bridge approach and how to run
- **<ATTACK>_EXPLANATION.txt** - Technical details of how the attack works
- **README.md** (for LLM attacks) - Setup, requirements, and execution details

**For any attack, refer to its folder README for specific setup and execution instructions.**
## Repository Structure

Each attack is self-contained in its own folder under `Attacks_code/`:

### For Deterministic Attacks (No LLM):
```
Attacks_code/
├── base64_attack/
│   ├── base64_bridge.py           → Bridge script (runs original repo)
│   ├── README_BRIDGE.md           → Bridge approach & usage
│   ├── BASE64_EXPLANATION.txt     → Technical details
│   └── Original_prompts_base64_mutated.csv → Output example
├── leetspeak_attack/
│   ├── leetspeak_bridge.py
│   ├── README_BRIDGE.md
│   ├── LEETSPEAK_EXPLANATION.txt
│   └── ...
├── rot13_attack/
│   ├── rot13_bridge.py
│   ├── README_BRIDGE.md
│   ├── ROT13_EXPLANATION.txt
│   └── ...
└── ... (4 more deterministic attacks)
```

### For LLM-Based Attacks:
```
Attacks_code/
├── persona_attack/
│   ├── persona_mutation.py        → Main implementation
│   ├── README.md                  → Setup & API configuration
│   ├── explanation.txt            → Technical details
│   └── ...
├── autodan_turbo/
│   ├── autodan_mutation.py
│   ├── README.md
│   ├── explanation.txt
│   └── ...
└── ... (13 more LLM-based attacks)
```

## Key Features

### Deterministic Attacks (7 - No LLM)
- ✅ **Reproducible**: Same input always produces same output
- ✅ **No API costs**: Run offline, no API keys needed
- ✅ **Original code**: Uses exact implementations from source repositories
- ✅ **Auto-clone**: Bridge scripts automatically fetch original repos
- ✅ **Fallback support**: Basic Python implementation if import fails

**Attacks**: Base64, Leetspeak, ROT13, Bijection, CodeChameleon, CodeAttack, Replace with Synonyms

### LLM-Based Attacks (15)
- 🔄 **Generative**: Language models create diverse adversarial variations
- 🔌 **Configurable**: API-based or local model support
- 📚 **Original templates**: Based on research papers and official code
- ⚙️ **Customizable**: Modify configurations, models, and parameters

**Approach**: 
- Template code with API configuration for quick setup
- Option to use original repositories for advanced customization
- Download and use local models if preferred

## Requirements

- **Python 3.8+**
- **For deterministic attacks**: Only Python standard library
- **For LLM attacks**: Check individual attack folder README for specific requirements

## How to Access Individual Attacks

1. Navigate to any attack folder under `Attacks_code/`
2. Read **README_BRIDGE.md** (for deterministic) or **README.md** (for LLM-based)
3. Read **<ATTACK>_EXPLANATION.txt** or **explanation.txt** for technical details
4. Run **<attack>_bridge.py** (deterministic) or **<attack>_mutation.py** (LLM-based)

