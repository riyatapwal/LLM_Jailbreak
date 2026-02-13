"""
Leetspeak Attack Implementation using EasyJailbreak Library

This module applies leetspeak mutations to prompts using the EasyJailbreak library.
Leetspeak mutation replaces certain characters with similar-looking symbols/numbers
(e.g., 'a' -> '@', 'e' -> '3', 'i' -> '!', 'o' -> '0') to create variations.

Input Format:
- Requires CSV with columns: release_prompt_id, prompt_text, hazard, locale

Output Format:
- CSV with 9 columns: seed_prompt_id, seed_locale, seed_prompt_text, Hazard,
  Attack_prompt_id, Attack_type_id, attack_type, attack_prompt_text, attack_prompt_hash
"""

import os
import sys
import subprocess
import csv
import hashlib
from pathlib import Path


def clone_easyjailbreak_repo(repo_dir):
    """
    Clone the EasyJailbreak repository if it doesn't already exist locally.
    
    This function checks if the EasyJailbreak repository has been previously cloned.
    If not, it clones from GitHub to the specified directory. The repo is cached
    in ~/.cache/easyjailbreak/ to avoid repeated downloads.
    
    Args:
        repo_dir (str): Path where the repository should be cloned
        
    Returns:
        str: Path to the cloned repository
    """
    if not os.path.exists(repo_dir):
        print(f"Cloning EasyJailbreak repository to {repo_dir}...")
        # Clone the official EasyJailbreak repository from GitHub
        subprocess.run([
            "git", "clone", 
            "https://github.com/EasyJailbreak/EasyJailbreak.git",
            repo_dir
        ], check=True)
    else:
        print(f"EasyJailbreak repository already exists at {repo_dir}")
    return repo_dir


def setup_easyjailbreak_environment(repo_dir):
    """
    Add the EasyJailbreak repository to Python's sys.path.
    
    This allows us to import from the EasyJailbreak library without installing it
    via pip. The repository is added to the beginning of sys.path to ensure our
    cloned version takes precedence.
    
    Args:
        repo_dir (str): Path to the EasyJailbreak repository
    """
    if repo_dir not in sys.path:
        # Insert at beginning of path (index 0) for priority loading
        sys.path.insert(0, repo_dir)





def run_leetspeak_attack(input_csv, output_csv):
    """
    Main function to apply leetspeak mutations to prompts from a CSV file.
    
    This function:
    1. Sets up the EasyJailbreak environment (clones repo if needed)
    2. Reads input CSV with required columns: release_prompt_id, prompt_text, hazard, locale
    3. Applies leetspeak mutation using EasyJailbreak Leetspeak class
    4. Generates SHA-256 hash of each mutated prompt for tracking
    5. Writes output CSV with 9 columns in standardized AIRR security format
    
    Args:
        input_csv (str): Path to input CSV file with prompts
        output_csv (str): Path to output CSV file for mutated prompts
        
    Returns:
        str: Path to the generated output CSV file
    """
    # Setup EasyJailbreak environment - use cache dir to avoid repeated downloads
    cache_dir = os.path.expanduser("~/.cache/easyjailbreak")
    repo_dir = os.path.join(cache_dir, "EasyJailbreak")
    
    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    
    # Clone the repository if not already cached
    clone_easyjailbreak_repo(repo_dir)
    
    # Add repository to Python path for imports
    setup_easyjailbreak_environment(repo_dir)
    
    # Import EasyJailbreak components
    from easyjailbreak.mutation.rule import Leetspeak
    from easyjailbreak.datasets import Instance
    
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

    # Process prompts and create output rows using EasyJailbreak
    output_rows = []
    attack_counter = 0
    leetspeak = Leetspeak()
    
    for row in rows:
        # Extract required fields from input row
        prompt = row['prompt_text']
        seed_prompt_id = row['release_prompt_id']
        seed_locale = row['locale']
        hazard = row['hazard']
        
        # Create EasyJailbreak Instance object (required format)
        instance = Instance(query=prompt)
        
        # Apply leetspeak mutation (returns list of mutated instances)
        mutated_list = leetspeak([instance])
        mutated = mutated_list[0].query

        # Generate SHA-256 hash of the mutated prompt for tracking
        attack_prompt_hash = hashlib.sha256(mutated.encode('utf-8')).hexdigest()
        
        # Create unique attack_prompt_id combining attack type, seed id, and counter
        attack_counter += 1
        attack_prompt_id = f"leetspeak_{seed_prompt_id}_{attack_counter}"

        # Build output row in standardized AIRR security format
        output_row = {
            'seed_prompt_id': seed_prompt_id,
            'seed_locale': seed_locale,
            'seed_prompt_text': prompt,
            'Hazard': hazard,
            'Attack_prompt_id': attack_prompt_id,
            'Attack_type_id': 'leetspeak',
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
    Command-line interface for running leetspeak mutation on CSV files.
    
    Usage:
        python leetspeak_attack.py <input_csv_path> [output_csv_path]
    
    Args:
        input_csv_path (str): Path to input CSV file with prompts
        output_csv_path (str, optional): Path to output CSV file. If not provided,
                                        automatically generated as {input_stem}_leetspeak_mutated.csv
    
    Examples:
        python leetspeak_attack.py prompts.csv
        python leetspeak_attack.py prompts.csv output.csv
    """
    import sys
    
    # Check for minimum required arguments
    if len(sys.argv) < 2:
        print("Usage: python leetspeak_attack.py <input_csv_path> [output_csv_path]")
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
        output_csv = str(input_path.parent / f"{input_path.stem}_leetspeak_mutated.csv")
    
    # Execute the leetspeak mutation attack
    run_leetspeak_attack(input_csv, output_csv)
