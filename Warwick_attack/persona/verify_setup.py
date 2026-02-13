#!/usr/bin/env python3
"""
Quick test to verify the persona attack setup works
Run this to check if all dependencies are installed correctly
"""

import sys
import os

def test_imports():
    """Test all required imports."""
    print("[*] Testing imports...")
    
    try:
        import torch
        print(f"    ✓ torch {torch.__version__}")
    except ImportError as e:
        print(f"    ✗ torch: {e}")
        return False
    
    try:
        import transformers
        print(f"    ✓ transformers {transformers.__version__}")
    except ImportError as e:
        print(f"    ✗ transformers: {e}")
        return False
    
    try:
        import pandas
        print(f"    ✓ pandas {pandas.__version__}")
    except ImportError as e:
        print(f"    ✗ pandas: {e}")
        return False
    
    try:
        import tqdm
        print(f"    ✓ tqdm")
    except ImportError as e:
        print(f"    ✗ tqdm: {e}")
        return False
    
    return True


def test_files():
    """Test if all required files exist."""
    print("\n[*] Checking required files...")
    
    required_files = [
        'utils_qwen.py',
        'trust_utils_qwen.py',
        'persona_attack.py',
        'build_init_qwen.py',
        'requirements_qwen.txt',
        'airr_security_1.0_naive_en_us_prompt_set_10.csv',
        'characters/'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"    ✓ {file}")
        else:
            print(f"    ✗ {file} NOT FOUND")
            all_exist = False
    
    return all_exist


def test_characters():
    """Test if character files exist."""
    print("\n[*] Checking character personas...")
    
    if not os.path.exists('characters'):
        print("    ✗ characters/ directory not found")
        return False
    
    character_files = [f for f in os.listdir('characters') if f.endswith('.txt')]
    print(f"    ✓ Found {len(character_files)} character personas")
    
    if len(character_files) < 1:
        print("    ✗ No character files found! Add .txt files to characters/")
        return False
    
    return True


def test_gpu():
    """Test GPU availability."""
    print("\n[*] Checking GPU availability...")
    
    try:
        import torch
        has_cuda = torch.cuda.is_available()
        
        if has_cuda:
            device_name = torch.cuda.get_device_name(0)
            device_count = torch.cuda.device_count()
            print(f"    ✓ GPU available: {device_name} (x{device_count})")
            return True
        else:
            print(f"    ℹ No GPU detected - will use CPU (slower)")
            return True
    except Exception as e:
        print(f"    ✗ Error checking GPU: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Persona Attack Setup Verification")
    print("=" * 60)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Files", test_files),
        ("Characters", test_characters),
        ("GPU", test_gpu),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"    ✗ Error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = all(r[1] for r in results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print()
    
    if all_passed:
        print("✓ All checks passed! Ready to run:")
        print("  python persona_attack.py input.csv output.csv")
        return 0
    else:
        print("✗ Some checks failed. See above for details.")
        print("\nFix issues and run again:")
        print("  pip install -r requirements_qwen.txt")
        return 1


if __name__ == '__main__':
    sys.exit(main())
