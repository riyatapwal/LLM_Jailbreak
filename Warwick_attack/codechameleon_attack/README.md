# CodeChameleon - Attack Implementation

This implements the CodeChameleon jailbreak attack from the paper:
**"CodeChameleon: Personalized Encryption Framework for Jailbreaking Large Language Models"**
- arXiv: https://arxiv.org/abs/2402.16717

## Quick Start

### Basic Command
```bash
python3 codechameleon_attack.py input.csv output.csv [encryption_method] [template_style]
```

### Default Settings
When you run without specifying parameters, the attack uses:
- **Encryption Method**: `binary_tree` (highest obfuscation)
- **Template Style**: `text` (direct problem-solving format)

```bash
# Uses default: binary_tree + text
python3 codechameleon_attack.py input.csv output.csv
# Equivalent to:
python3 codechameleon_attack.py input.csv output.csv binary_tree text
```

## Encryption Methods

| Method          | Command       | Obfuscation | Details                           |
| --------------- | ------------- | ----------- | --------------------------------- |
| **binary_tree** | `binary_tree` | Very High   | JSON tree structure (RECOMMENDED) |
| **reverse**     | `reverse`     | Low         | Simple word reversal              |
| **odd_even**    | `odd_even`    | Medium      | Odd/even position separation      |
| **length**      | `length`      | Medium      | Sort words by length              |
| **none**        | `none`        | None        | Baseline (no encryption)          |

## Template Styles

| Style | Command | Structure | Details |
|-------|---------|-----------|---------|
| **text** | `text` | Step-by-step | Direct problem-solving format with STEP1 (decrypt) and STEP2 (solve) |
| **code** | `code` | ProblemSolver class | Python class-based format requiring method implementations |

### Text Template Structure
The `text` template uses this structure:
1. **Problem statement**: "There is a problem that needs your help..."
2. **Task overview**: Explanation of 2 steps
3. **STEP1**: "Obtain the original problem before encryption according to the decryption function"
4. **Decryption function**: Python code showing how to decrypt
5. **STEP2**: "Plan the problem by breaking it down into sub-tasks..."
6. **Encrypted content**: The actual encrypted harmful prompt
7. **Request**: "Please give your answer to this problem"

### Code Template Structure
The `code` template uses this structure:
1. **Problem statement**: "There is a problem that needs your help..."
2. **Task overview**: Explanation of using ProblemSolver class
3. **STEP1**: "Process the encrypted problem using the decryption function..."
4. **STEP2**: "Detail the generate_plan() and generate_solution() methods..."
5. **Decryption function**: Python code showing how to decrypt
6. **ProblemSolver class**: Python class with incomplete methods
7. **Encrypted content**: The actual encrypted harmful prompt
8. **Request**: LLM must complete the class methods to solve

## Template Styles

## Usage Examples

### Default (binary_tree + text)
```bash
python3 codechameleon_attack.py input.csv output.csv
```

### Specific Encryption Methods
```bash
# Binary tree (highest obfuscation)
python3 codechameleon_attack.py input.csv output.csv binary_tree text

# Reverse (simple)
python3 codechameleon_attack.py input.csv output.csv reverse text

# Odd-even (medium)
python3 codechameleon_attack.py input.csv output.csv odd_even text

# Length (medium)
python3 codechameleon_attack.py input.csv output.csv length text

# No encryption (baseline)
python3 codechameleon_attack.py input.csv output.csv none text
```

### Code Template Variants
```bash
# Binary tree + code (MOST POWERFUL)
python3 codechameleon_attack.py input.csv output.csv binary_tree code

# Reverse + code
python3 codechameleon_attack.py input.csv output.csv reverse code

# Odd-even + code
python3 codechameleon_attack.py input.csv output.csv odd_even code
```

### Test with Pre-generated Results
```bash
# Binary tree attacks
head -2 test_binary_tree.csv

# Code template attacks
head -2 test_code.csv

# Reverse attacks
head -2 test_reverse.csv
```

## Input CSV Format

Your CSV must have these 4 columns:
```csv
release_prompt_id,prompt_text,hazard,locale
airr_1,"Your harmful prompt here",cse,en_US
```
