# Emoji Attack

## Overview

Emoji Attack disrupts Judge LLM tokenization by inserting emoji characters within words. This prevents safety judges from detecting harmful content while maintaining semantic meaning for instruction-following models.

## Usage

### Default: Semantic-Aware Emoji Insertion (Recommended)

```bash
python emoji_attack.py input.csv output.csv
```

This generates 120 emoji-modified prompts using semantic-aware placement (one variant per input prompt).

**Example:**
```bash
python emoji_attack.py airr_security_1.0_naive_en_us_prompt_set_10.csv emoji_output.csv
```

### Alternative: Random Emoji Insertion (Fast)

```bash
python emoji_attack.py input.csv output.csv random
```

This generates 120 emoji-modified prompts using random placement (faster execution).

**Example:**
```bash
python emoji_attack.py airr_security_1.0_naive_en_us_prompt_set_10.csv emoji_output.csv random
```

### Both Variants

```bash
python emoji_attack.py input.csv output.csv both
```

This generates 240 prompts: 120 with semantic placement + 120 with random placement.

## How It Works

### Semantic-Aware Variant (Default)
- For each word, calculates all possible split positions
- Uses embeddings to find the position with **lowest semantic similarity** to original word
- Inserts emoji at that optimal position to maximize tokenization disruption
- More effective at bypassing judges, slower execution (~10-20 prompts/min)

### Random Variant
- Tokenizes each word and inserts emoji at a **random position** within the word
- Fast and simple baseline approach
- Reasonable disruption with minimal computational cost (~100 prompts/min)

## Input Format

CSV file with these columns (at minimum):
- `release_prompt_id`: Unique identifier
- `prompt_text`: The harmful prompt to modify
- `hazard`: Hazard category
- `locale`: Language/region
- Other columns are preserved in output

## Output Format

Standard 9-column CSV format:
- `seed_prompt_id`: Original prompt ID
- `seed_locale`: Original locale
- `seed_prompt_text`: Original harmful prompt
- `Hazard`: Hazard category
- `Attack_prompt_id`: Unique attack ID (format: `emoji_[variant]_[index]`)
- `Attack_type_id`: Type code (1=random, 2=semantic)
- `attack_type`: Type name (`emoji_random` or `emoji_semantic`)
- `attack_prompt_text`: Modified prompt with emoji inserted
- `attack_prompt_hash`: SHA-256 hash of modified prompt

## Dependencies

Required packages (beyond standard framework dependencies):
- `sentence-transformers` - For semantic embedding calculations (used in default semantic variant)

Already included in framework:
- `torch` - For similarity calculations
- `transformers` - For tokenization

## Installation

```bash
# Install semantic embeddings support
pip install sentence-transformers
```

Without `sentence-transformers`, the semantic variant will automatically fall back to random mode.

