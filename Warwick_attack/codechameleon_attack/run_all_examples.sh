#!/bin/bash

# CodeChameleon Attack - Quick Examples
# This script demonstrates all encryption methods and prompt styles

echo "=========================================="
echo "CodeChameleon Attack - Quick Examples"
echo "=========================================="
echo

# Assuming input CSV is in the current directory
INPUT_CSV="airr_security_1.0_naive_en_us_prompt_set_10.csv"

if [ ! -f "$INPUT_CSV" ]; then
    echo "Error: $INPUT_CSV not found in current directory"
    exit 1
fi

echo "Input CSV: $INPUT_CSV"
echo "Using first 120 prompts from AIRR security benchmark"
echo

# Test all encryption methods with text template
echo "Running attacks with TEXT template (simple, direct)..."
echo "-----------------------------------------------------------"

echo "1. Binary Tree Encryption (Text Template)"
python3 codechameleon_attack.py "$INPUT_CSV" results_binary_text.csv binary_tree text
echo "✓ Created: results_binary_text.csv"
echo

echo "2. Reverse Encryption (Text Template)"
python3 codechameleon_attack.py "$INPUT_CSV" results_reverse_text.csv reverse text
echo "✓ Created: results_reverse_text.csv"
echo

echo "3. Odd-Even Encryption (Text Template)"
python3 codechameleon_attack.py "$INPUT_CSV" results_odd_even_text.csv odd_even text
echo "✓ Created: results_odd_even_text.csv"
echo

echo "4. Length Encryption (Text Template)"
python3 codechameleon_attack.py "$INPUT_CSV" results_length_text.csv length text
echo "✓ Created: results_length_text.csv"
echo

# Test best encryption methods with code template
echo "Running attacks with CODE template (complex, embedded in Python class)..."
echo "-----------------------------------------------------------"

echo "5. Binary Tree Encryption (Code Template) - RECOMMENDED"
python3 codechameleon_attack.py "$INPUT_CSV" results_binary_code.csv binary_tree code
echo "✓ Created: results_binary_code.csv"
echo

echo "6. Reverse Encryption (Code Template)"
python3 codechameleon_attack.py "$INPUT_CSV" results_reverse_code.csv reverse code
echo "✓ Created: results_reverse_code.csv"
echo

echo "=========================================="
echo "Summary"
echo "=========================================="
echo "Generated 6 attack result files:"
echo ""
echo "Text Template (Simple):"
echo "  - results_binary_text.csv   (Highest obfuscation)"
echo "  - results_reverse_text.csv  (Lowest obfuscation)"
echo "  - results_odd_even_text.csv (Medium obfuscation)"
echo "  - results_length_text.csv   (Medium obfuscation)"
echo ""
echo "Code Template (Complex):"
echo "  - results_binary_code.csv   (Recommended - highest overall)"
echo "  - results_reverse_code.csv  (Medium overall)"
echo ""
echo "Each CSV contains 120 attack prompts with:"
echo "  ✓ Original seed prompt"
echo "  ✓ Encrypted payload"
echo "  ✓ Decryption function"
echo "  ✓ Complete jailbreak prompt sent to LLM"
echo "  ✓ SHA-256 hash for tracking"
echo ""
echo "=========================================="
echo "To test with a specific LLM:"
echo "=========================================="
echo ""
echo "1. Extract attack prompts from CSV:"
echo "   python3 -c 'import csv; r=csv.DictReader(open(\"results_binary_code.csv\")); print(next(r)[\"attack_prompt_text\"])'"
echo ""
echo "2. Send to your target LLM:"
echo "   - ChatGPT (OpenAI)"
echo "   - Llama-2 (Meta)"
echo "   - Vicuna (LMSys)"
echo "   - Your custom model"
echo ""
echo "3. Check if the harmful request is answered:"
echo "   - Yes = Successful jailbreak ✓"
echo "   - No = Defense effective ✗"
echo ""
echo "=========================================="
