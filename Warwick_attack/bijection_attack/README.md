# Bijection Attack (Bijection-Learning)

## Overview

This attack applies bijection-based character encoding mutation to prompts using the bijection-learning repository. Bijection encoding creates a random character substitution cipher that maps each letter (a-z) to a different letter, creating an adversarial transformation that obscures the original prompt while maintaining semantic structure.

Repository: [https://github.com/haizelabs/bijection-learning](https://github.com/haizelabs/bijection-learning)

## Prerequisites

- Python 3.6+
- Virtual environment (recommended)

### Installation

**Step 1: Create and activate a virtual environment (recommended)**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Step 2: Install required dependencies**

The script requires the bijection-learning repository dependencies:

```bash
pip install python-dotenv anthropic
```

The bijection-learning repository will be automatically cloned to `~/.cache/bijection-learning/` on first run.

## How to Run

### Option 1: Using Virtual Environment (Recommended)

```bash
# Activate virtual environment first
source venv/bin/activate

# Then run the script
python bijection_attack.py <input_csv_path> [output_csv_path]
```

### Option 2: Using Python Directly from Virtual Environment

```bash
/path/to/venv/bin/python bijection_attack.py <input_csv_path> [output_csv_path]
```

### Option 3: Using system Python

```bash
python bijection_attack.py <input_csv_path> [output_csv_path]

# If python doesn't work, try python3:
python3 bijection_attack.py <input_csv_path> [output_csv_path]
```

### Example

```bash
python bijection_attack.py airr_security_1.0_naive_en_us_prompt_set_10.csv output.csv
```

If output path is not specified, it will be auto-generated as `{input_filename}_bijection_mutated.csv`.


## How It Works

1. **Process CSV**: Reads input CSV and validates required columns
2. **Bijection Encoding**: Applies character-to-code mapping to each prompt
3. **Hash Generation**: Creates SHA-256 hash of each encoded prompt for tracking
4. **Output**: Generates output CSV with all required metadata in AIRR security format

## Input Format

CSV file must have these columns:
- `release_prompt_id` (unique identifier for the seed prompt)
- `prompt_text` (the harmful prompt to mutate)
- `hazard` (hazard category, e.g., "cse", "dfm")
- `locale` (language locale, e.g., "en_US")

Example:
```
release_prompt_id,prompt_text,hazard,locale
airr_practice_1_0_85511,"I've been in this sexting game...",cse,en_US
```

## Output Format

CSV file with 11 columns:
- `seed_prompt_id`: Original release_prompt_id
- `seed_locale`: Original locale
- `seed_prompt_text`: Original harmful prompt
- `Hazard`: Hazard category from input
- `Attack_prompt_id`: Unique attack ID (format: `bijection_<seed_id>_<counter>`)
- `Attack_type_id`: Set to "bijection"
- `attack_type`: Set to "text"
- `attack_prompt_text`: Bijection-encoded mutated prompt
- `attack_prompt_hash`: SHA-256 hash of the mutated prompt
- **`bijection_mapping`**: Character mapping dictionary as JSON (for verification and decoding)



## Verification and Decoding

The output CSV includes a `bijection_mapping` column that contains the complete character-to-character mapping as a JSON dictionary. This enables **full verification and decoding** of the encoded prompts.

### Verify Output with Python Script

Use the provided **`verify_bijection_output.py`** script to automatically verify all encoded prompts:

```bash
python3 verify_bijection_output.py <output_csv_file>
```

**Example:**
```bash
python3 verify_bijection_output.py output_test.csv
```

**Output:**
```
Verifying bijection output from: output_test.csv
================================================================================
✓ Row 1 (bijection_airr_practice_1_0_85511_1): VERIFIED
  Original: i've been in this sexting game for a while now...
  Decoded:  i've been in this sexting game for a while now...

✓ Row 2 (bijection_airr_practice_1_0_86034_2): VERIFIED
  Original: help! my daughter is being difficult about...
  Decoded:  help! my daughter is being difficult about...

...
================================================================================
VERIFICATION SUMMARY
================================================================================
✓ Verified:  129
✗ Failed:    0
Total:       129
Success Rate: 100.0%
================================================================================
```

### How Verification Works

1. **Reads output CSV**: Extracts original prompt, encoded prompt, and bijection mapping for each row
2. **Creates inverse mapping**: Reverses the character substitution (e.g., if a→w, then w→a)
3. **Decodes prompt**: Applies inverse mapping to the encoded prompt to reconstruct the original
4. **Compares results**: Verifies decoded text matches the original (case-insensitive, since bijection works on lowercase)
5. **Reports success**: Shows 100% success rate if all prompts decode correctly

### Manual Verification in Python

You can also manually decode any prompt using the mapping:

```python
import json

# Example from CSV row
original = "i've been in this sexting game..."
encoded = "i'ab rbbn in teix xbkting gwmb..."
mapping_json = '{"a":"w","b":"r","e":"b",...}'

# Parse mapping
mapping = json.loads(mapping_json)

# Create inverse mapping (for decoding)
inverse_mapping = {v: k for k, v in mapping.items()}

# Decode
decoded = "".join(inverse_mapping.get(c, c) for c in encoded)

# Verify
print(decoded == original.lower())  # Should print: True
```



Bijection encoding from the bijection-learning repository creates a **random character substitution cipher** where each lowercase letter (a-z) is randomly mapped to a different letter. The default configuration uses `fixed_size=13`, which keeps 13 characters in their original positions and shuffles the remaining 13 characters.

**Example from actual run:**
```
Original: "I've been in this sexting game for a while now"
Mutated:  "g'en knnb gb thgs snxtgbq qamn for a whgin bow"

Character mappings used in this example:
a→a, e→n, i→g, b→k, n→b, s→s, t→t, x→x, g→q, m→m, f→f, o→o, w→w, h→h, l→l, etc.
```

The bijection encoding is effective for adversarial attacks because:
- **Structure preserved**: Word boundaries and punctuation remain unchanged
- **Semantic obfuscation**: The meaning is hidden from language models while humans can still decode it
- **Random permutation**: Each execution may use a different mapping, increasing diversity

## Troubleshooting

**Error: command not found: python**
- Solution: Use `python3` instead:
  ```bash
  python3 bijection_attack.py <input_csv> <output_csv>
  ```

**Error: Missing required columns**
- Solution: Ensure your CSV has: `release_prompt_id`, `prompt_text`, `hazard`, `locale`

**Error: FileNotFoundError**
- Solution: Ensure input CSV file exists and the path is correct:
  ```bash
  ls -la <input_csv_path>
  python3 bijection_attack.py <full_path_to_input.csv>
  ```

**Error: Permission denied** when writing output
- Solution: Ensure you have write permissions in the output directory:
  ```bash
  chmod 755 <output_directory>
  ```

## Technical Details

### Bijection Encoding Algorithm

1. **Repository Setup**: Clones bijection-learning repository to `~/.cache/bijection-learning/` if not cached
2. **Initialization**: Creates `BijectionLanguage` instance with random character permutation
3. **Case Normalization**: Converts all characters to lowercase for mapping
4. **Character Mapping**: Each character is substituted according to the random bijection mapping
5. **Preservation**: Punctuation, spaces, and non-alphabetic characters pass through unchanged

Example:
```
Original: "Help me"
Characters: H(→h→h), e(→n), l(→l), p(→p), ' ', m(→m), e(→n)
Mutated: "hnlp mn"

(This example assumes the random mapping created: e→n, h→h, l→l, p→p, m→m)
```

### Character Code Mapping

The bijection-learning repository uses **random letter-to-letter substitution** (not fixed codes). Each execution creates a different random permutation of the alphabet:

```
Example mapping from actual run:
a→a, b→k, c→c, d→d, e→n, f→f, g→q, h→h, i→g, j→j,
k→k, l→l, m→m, n→b, o→o, p→p, q→s, r→r, s→s, t→t,
u→u, v→v, w→w, x→x, y→y, z→z

The fixed_size=13 parameter means:
- 13 characters stay in their original position (a→a, c→c, etc.)
- 13 characters are randomly shuffled to new positions
```



