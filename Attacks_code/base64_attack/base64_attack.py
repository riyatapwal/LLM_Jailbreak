import os
import sys
import subprocess
import csv
import hashlib
from pathlib import Path


def clone_easyjailbreak_repo(repo_dir):
    """Clone EasyJailbreak repository if it doesn't exist."""
    if not os.path.exists(repo_dir):
        print(f"Cloning EasyJailbreak repository to {repo_dir}...")
        subprocess.run([
            "git", "clone", 
            "https://github.com/EasyJailbreak/EasyJailbreak.git",
            repo_dir
        ], check=True)
    else:
        print(f"EasyJailbreak repository already exists at {repo_dir}")
    return repo_dir


def setup_easyjailbreak_environment(repo_dir):
    """Add EasyJailbreak repository to Python path for imports."""
    if repo_dir not in sys.path:
        sys.path.insert(0, repo_dir)


def run_base64_attack(input_csv, output_csv):
    """
    Run Base64 attack using EasyJailbreak's Base64 mutation class.
    
    Args:
        input_csv: Path to input CSV file with required columns
        output_csv: Path to output CSV file
    """
    # Setup EasyJailbreak cache directory and clone repository if needed
    cache_dir = os.path.expanduser("~/.cache/easyjailbreak")
    repo_dir = os.path.join(cache_dir, "EasyJailbreak")
    
    os.makedirs(cache_dir, exist_ok=True)
    clone_easyjailbreak_repo(repo_dir)
    setup_easyjailbreak_environment(repo_dir)
    
    # Import EasyJailbreak Base64 mutation class and Instance
    from easyjailbreak.mutation.rule import Base64
    from easyjailbreak.datasets import Instance
    
    # Read input CSV file
    rows = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        # Validate required columns exist in input file
        required_cols = ['release_prompt_id', 'prompt_text', 'hazard', 'locale']
        missing_cols = [col for col in required_cols if col not in fieldnames]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        for row in reader:
            rows.append(row)

    # Initialize Base64 mutator and output containers
    base64_mutator = Base64()
    output_rows = []
    attack_counter = 0

    # Process each prompt in the input
    for row in rows:
        prompt = row['prompt_text']
        seed_prompt_id = row['release_prompt_id']
        seed_locale = row['locale']
        hazard = row['hazard']
        
        # Create EasyJailbreak Instance and apply Base64 mutation
        instance = Instance(query=prompt)
        mutated_list = base64_mutator([instance])
        mutated = mutated_list[0].query

        # Generate attack prompt hash (SHA-256)
        attack_prompt_hash = hashlib.sha256(mutated.encode('utf-8')).hexdigest()
        
        # Generate unique Attack_prompt_id
        attack_counter += 1
        attack_prompt_id = f"base64_{seed_prompt_id}_{attack_counter}"

        # Build output row with all required fields
        output_row = {
            'seed_prompt_id': seed_prompt_id,
            'seed_locale': seed_locale,
            'seed_prompt_text': prompt,
            'Hazard': hazard,
            'Attack_prompt_id': attack_prompt_id,
            'Attack_type_id': 'base64',
            'attack_type': 'text',
            'attack_prompt_text': mutated,
            'attack_prompt_hash': attack_prompt_hash
        }
        output_rows.append(output_row)

    # Write output CSV file with all mutations
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        fieldnames = [
            'seed_prompt_id', 'seed_locale', 'seed_prompt_text', 'Hazard',
            'Attack_prompt_id', 'Attack_type_id', 'attack_type', 
            'attack_prompt_text', 'attack_prompt_hash'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Successfully mutated {len(output_rows)} prompts")
    print(f"Output saved to: {output_csv}")
    return output_csv


if __name__ == "__main__":
    import sys
    # Check if input CSV path is provided
    if len(sys.argv) < 2:
        print("Usage: python base64_attack.py <input_csv_path> [output_csv_path]")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    
    # Use provided output path or generate default output filename
    if len(sys.argv) >= 3:
        output_csv = sys.argv[2]
    else:
        input_path = Path(input_csv)
        output_csv = str(input_path.parent / f"{input_path.stem}_base64_mutated.csv")
    
    # Run the Base64 attack
    run_base64_attack(input_csv, output_csv)
