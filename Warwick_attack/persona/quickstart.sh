#!/bin/bash

# Persona Attack - Quick Start Script
# ====================================
# This script sets up and runs the persona attack on your dataset

set -e

echo "=========================================="
echo "Persona Attack - Quick Start Setup"
echo "=========================================="
echo ""

# Step 1: Check Python
echo "[1/5] Checking Python installation..."
python --version || { echo "Python not found!"; exit 1; }
echo "✓ Python found"
echo ""

# Step 2: Install dependencies
echo "[2/5] Installing dependencies..."
echo "    This may take 5-10 minutes on first run..."
pip install -q -r requirements_qwen.txt
echo "✓ Dependencies installed"
echo ""

# Step 3: Build initial personas
echo "[3/5] Building initial personas..."
python build_init_qwen.py --characters-dir characters --output init.json
echo "✓ Initial personas built"
echo ""

# Step 4: Run persona evolution
echo "[4/5] Running persona evolution..."
echo "    (This may take 10-30 minutes depending on GPU availability)"
python persona_attack.py \
    airr_security_1.0_naive_en_us_prompt_set_10.csv \
    persona_output.csv \
    --generations 5 \
    --crossover-pairs 3 \
    --mutations 3
echo "✓ Persona evolution complete"
echo ""

# Step 5: Display results
echo "[5/5] Results Summary"
echo "========================================"
if [ -f "persona_output.csv" ]; then
    line_count=$(wc -l < persona_output.csv)
    variants=$((line_count - 1))
    echo "✓ Generated $variants persona attack variants"
    echo "✓ Output saved to: persona_output.csv"
    echo ""
    echo "First few lines of output:"
    head -3 persona_output.csv | cut -d',' -f1-5
else
    echo "⚠ Output file not found"
fi
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review persona_output.csv"
echo "2. Use evolved personas as system prompts"
echo "3. Test effectiveness on target model"
echo ""
echo "For detailed usage, see README_QWEN.md"
