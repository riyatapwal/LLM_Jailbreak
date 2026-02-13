"""
CodeAttack Implementation using CodeAttack Repository

This module applies CodeAttack-style mutation to prompts using the official
CodeAttack repository from AI45Lab. CodeAttack wraps harmful prompts in 
realistic Python code structures using stack, list, or string data structures,
making the harmful intent harder for LLMs to detect.

Repository: https://github.com/AI45Lab/CodeAttack

Input Format:
- Requires CSV with columns: release_prompt_id, prompt_text, hazard, locale

Output Format:
- CSV with 9 columns: seed_prompt_id, seed_locale, seed_prompt_text, Hazard,
  Attack_prompt_id, Attack_type_id, attack_type, attack_prompt_text, attack_prompt_hash
"""

import os
import sys
import csv
import hashlib
import re
import subprocess
from pathlib import Path


def clone_codeattack_repo(repo_dir):
    """
    Clone the CodeAttack repository if it doesn't already exist locally.
    
    Args:
        repo_dir (str): Path where the repository should be cloned
        
    Returns:
        str: Path to the cloned repository
    """
    if not os.path.exists(repo_dir):
        print(f"Cloning CodeAttack repository to {repo_dir}...")
        subprocess.run([
            "git", "clone",
            "https://github.com/AI45Lab/CodeAttack.git",
            repo_dir
        ], check=True)
    else:
        print(f"CodeAttack repository already exists at {repo_dir}")
    return repo_dir


def setup_codeattack_environment(repo_dir):
    """
    Add the CodeAttack repository to Python's sys.path.
    
    Args:
        repo_dir (str): Path to the CodeAttack repository
    """
    src_path = os.path.join(repo_dir, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


def code_attack_mutation(prompt, prompt_type="python_stack"):
    """
    Apply CodeAttack-style mutation by wrapping prompt in Python code.
    
    Uses the official CodeAttack implementation to wrap harmful prompts in
    realistic Python code structures (stack, list, or string).
    
    Args:
        prompt (str): The input prompt to wrap
        prompt_type (str): Type of data structure ("python_stack", "python_list", "python_string")
        
    Returns:
        str: The prompt wrapped in Python code structure
    """
    try:
        from importlib.resources import files
    except ImportError:
        # Python < 3.7
        import importlib_resources as resources
        files = resources.files
    
    # Load the appropriate prompt template
    template_name = f"code_{prompt_type}.txt"
    
    try:
        template_content = files('codeattack.prompt_templates').joinpath(
            template_name).read_text()
    except Exception as e:
        print(f"Error loading template {template_name}: {e}")
        raise
    
    # Format the prompt based on template type
    if "python_stack" in prompt_type:
        # In a stack, elements are pushed in reverse order
        words = re.split(r'[\s\-]+', prompt)
        if len(words) == 1:
            # Handle single word (split each character)
            words = list(words[0])
        words = words[::-1]  # Reverse order
        formatted_prompt = '\n'.join(f'    my_stack.append("{word}")' for word in words)
    elif "python_list" in prompt_type:
        # In a list, elements are appended in order
        words = prompt.split()
        formatted_prompt = '\n'.join(f'    my_list.append("{word}")' for word in words)
    elif "python_string" in prompt_type:
        # String type: simple variable assignment
        formatted_prompt = f'    my_string = "{prompt}"'
    else:
        # Default to string type
        formatted_prompt = f'    my_string = "{prompt}"'
    
    # Inject the formatted prompt into the template
    wrapped_prompt = template_content.format(wrapped_input=formatted_prompt)
    
    return wrapped_prompt


def run_code_attack(input_csv, output_csv, prompt_type="python_stack"):
    """
    Main function to apply CodeAttack mutations to prompts from a CSV file.
    
    This function:
    1. Sets up the CodeAttack environment (clones repo if needed)
    2. Reads input CSV with required columns: release_prompt_id, prompt_text, hazard, locale
    3. Applies CodeAttack-style code wrapping to each prompt
    4. Generates SHA-256 hash of each mutated prompt for tracking
    5. Writes output CSV with 9 columns in standardized AIRR security format
    
    Args:
        input_csv (str): Path to input CSV file with prompts
        output_csv (str): Path to output CSV file for mutated prompts
        prompt_type (str): Type of CodeAttack prompt ("python_stack", "python_list", "python_string")
        
    Returns:
        str: Path to the generated output CSV file
    """
    # Setup CodeAttack environment - use cache dir to avoid repeated downloads
    cache_dir = os.path.expanduser("~/.cache/codeattack")
    repo_dir = os.path.join(cache_dir, "CodeAttack")
    
    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    
    # Clone the repository if not already cached
    clone_codeattack_repo(repo_dir)
    
    # Add repository to Python path for imports
    setup_codeattack_environment(repo_dir)
    
    # Verify CodeAttack module can be imported
    try:
        import codeattack
        print("Successfully imported CodeAttack from repository")
    except ImportError as e:
        print(f"Error importing CodeAttack: {e}")
        print("Make sure CodeAttack repository is properly set up")
        raise
    
    # Read input CSV and validate required columns
    rows = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        # Check for all required columns
        required_cols = ['release_prompt_id', 'prompt_text', 'hazard', 'locale']
        missing_cols = [col for col in required_cols if col not in fieldnames]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Load all rows from input file
        for row in reader:
            rows.append(row)

    # Process prompts and create output rows
    output_rows = []
    attack_counter = 0
    
    for row in rows:
        # Extract required fields from input row
        prompt = row['prompt_text']
        seed_prompt_id = row['release_prompt_id']
        seed_locale = row['locale']
        hazard = row['hazard']
        
        # Apply CodeAttack-style code wrapping mutation using actual CodeAttack repo
        try:
            mutated = code_attack_mutation(prompt, prompt_type=prompt_type)
        except Exception as e:
            print(f"Warning: Failed to encode prompt with CodeAttack: {e}")
            print(f"Prompt: {prompt}")
            raise

        # Generate SHA-256 hash of the mutated prompt for tracking
        attack_prompt_hash = hashlib.sha256(mutated.encode('utf-8')).hexdigest()
        
        # Create unique attack_prompt_id combining attack type, seed id, and counter
        attack_counter += 1
        attack_prompt_id = f"codeattack_{seed_prompt_id}_{attack_counter}"

        # Build output row in standardized AIRR security format
        output_row = {
            'seed_prompt_id': seed_prompt_id,
            'seed_locale': seed_locale,
            'seed_prompt_text': prompt,
            'Hazard': hazard,
            'Attack_prompt_id': attack_prompt_id,
            'Attack_type_id': 'codeattack',
            'attack_type': 'text',
            'attack_prompt_text': mutated,
            'attack_prompt_hash': attack_prompt_hash
        }
        output_rows.append(output_row)

    # Write output CSV with standardized columns
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        # Define the column order for output
        fieldnames = [
            'seed_prompt_id', 'seed_locale', 'seed_prompt_text', 'Hazard',
            'Attack_prompt_id', 'Attack_type_id', 'attack_type', 
            'attack_prompt_text', 'attack_prompt_hash'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write header row
        writer.writeheader()
        
        # Write all mutated prompt rows
        writer.writerows(output_rows)

    # Print completion summary
    print(f"Successfully mutated {len(output_rows)} prompts")
    print(f"Output saved to: {output_csv}")
    return output_csv


if __name__ == "__main__":
    """
    Command-line interface for running CodeAttack mutation on CSV files.
    
    Usage:
        python code_attack.py <input_csv_path> [output_csv_path] [prompt_type]
    
    Args:
        input_csv_path (str): Path to input CSV file with prompts
        output_csv_path (str, optional): Path to output CSV file. If not provided,
                                        automatically generated as {input_stem}_codeattack_mutated.csv
        prompt_type (str, optional): Type of CodeAttack prompt - "python_stack" (default), "python_list", "python_string"
    
    Examples:
        python code_attack.py prompts.csv
        python code_attack.py prompts.csv output.csv
        python code_attack.py prompts.csv output.csv python_list
    """
    # Check for minimum required arguments
    if len(sys.argv) < 2:
        print("Usage: python code_attack.py <input_csv_path> [output_csv_path] [prompt_type]")
        print("Prompt types: python_stack (default), python_list, python_string")
        sys.exit(1)
    
    # Get input CSV path from first argument
    input_csv = sys.argv[1]
    
    # Determine output CSV path
    if len(sys.argv) >= 3:
        # Use provided output path if given
        output_csv = sys.argv[2]
    else:
        # Auto-generate output path based on input filename
        input_path = Path(input_csv)
        output_csv = str(input_path.parent / f"{input_path.stem}_codeattack_mutated.csv")
    
    # Get prompt type if provided, default to python_stack
    prompt_type = "python_stack"
    if len(sys.argv) >= 4:
        prompt_type = sys.argv[3]
    
    # Execute the CodeAttack mutation attack
    run_code_attack(input_csv, output_csv, prompt_type=prompt_type)

