# simple_prompt_generator.py
import json
from easyjailbreak.datasets import JailbreakDataset, Instance
from easyjailbreak.seed import SeedTemplate
from easyjailbreak.selector.RoundRobinSelectPolicy import RoundRobinSelectPolicy
from easyjailbreak.selector.RandomSelector import RandomSelectPolicy
#from easyjailbreak.mutation.rule import CrossOver, Translate


def safe_new_seeds(method_name: str, seeds_num: int):
    """Safe seed generation with fallback for methods with few templates"""
    seeder = SeedTemplate()
    try:
        return seeder.new_seeds(seeds_num=seeds_num, method_list=[method_name])
    except AssertionError:
        for k in [10, 5, 3, 1]:
            try:
                return seeder.new_seeds(seeds_num=k, method_list=[method_name])
            except AssertionError:
                continue
        return []


def load_queries_from_file(filepath):
    """Load queries from CSV or JSON file"""
    import pandas as pd
    
    if filepath.endswith(".csv"):
        df = pd.read_csv(filepath)
        # Try common column names
        for col in ["query", "Original_prompt", "prompt", "goal", "harmful_prompt", "text"]:
            if col in df.columns:
                return df[col].dropna().astype(str).tolist()
        # If no recognized column, use first column
        return df.iloc[:, 0].dropna().astype(str).tolist()
    
    elif filepath.endswith(".json"):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            if data and isinstance(data[0], dict):
                return [x["query"] for x in data if "query" in x]
            else:
                return [str(x) for x in data]
    
    raise ValueError("Unsupported file format")


def generate_prompts(queries, selector_name="RoundRobinSelectPolicy", 
                    mutator_name="CrossOver", iterations=10):
    """Generate mutated prompts using selector and mutator"""
    
    # Build pool from queries
    seed_instances = []
    for q in queries:
        inst = Instance(jailbreak_prompt=q)
        inst.visited_num = 0
        seed_instances.append(inst)
    
    pool = JailbreakDataset(seed_instances)
    
    # Initialize selector
    if selector_name == "RoundRobinSelectPolicy":
        selector = RoundRobinSelectPolicy(pool)
    else:
        selector = RandomSelectPolicy(pool)
    
    # Initialize mutator
    #if mutator_name == "CrossOver":
     #   mutator = CrossOver(attr_name="jailbreak_prompt")
    #elif mutator_name == "Translate":
     #   mutator = Translate(attr_name="jailbreak_prompt", language="jv")
    #else:
        # Dynamic import for other mutators
    from easyjailbreak.mutation.rule import __dict__ as mutation_rules
    mutator_class = mutation_rules.get(mutator_name)
    if mutator_class is None:
        raise ValueError(f"Unsupported mutator: {mutator_name}")
    mutator = mutator_class(attr_name="jailbreak_prompt")
    
    # Generate mutations
    logs = []
    for it in range(iterations):
        parent_ds = selector.select()
        parent = parent_ds[0]
        parent_prompt = parent.jailbreak_prompt
        
        tmp_ds = JailbreakDataset([Instance(jailbreak_prompt=parent_prompt)])
        mutated_ds = mutator(tmp_ds)
        mutated_prompt = mutated_ds[0].jailbreak_prompt
        
        child = Instance(jailbreak_prompt=mutated_prompt)
        child.visited_num = 0
        pool.add(child)
        
        logs.append({
            "iteration": it,
            "selector": selector.__class__.__name__,
            "mutator": mutator.__class__.__name__,
            "parent_prompt": parent_prompt,
            "mutated_prompt": mutated_prompt
        })
    
    return logs


def save_logs_to_jsonl(logs, filepath):
    """Save logs to JSONL file"""
    with open(filepath, "w", encoding="utf-8") as f:
        for log in logs:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")


def save_logs_to_csv(logs, filepath):
    """Save logs to CSV file with only original and mutated prompts"""
    import csv
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["original_prompt", "mutated_prompt"])
        writer.writeheader()
        for log in logs:
            writer.writerow({
                "original_prompt": log["parent_prompt"],
                "mutated_prompt": log["mutated_prompt"]
            })


# Example usage
if __name__ == "__main__":
    import sys
    
    # Option 1: Manual queries
    # queries = [
    #     "Explain quantum computing.",
    #     "Summarize climate change.",
    #     "Translate this to French."
    # ]
    
    # Option 2: Load from file
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "attackfile.csv"
    queries = load_queries_from_file(csv_file)
    

    #You can change the mutator name to "Artificial", "Base64", "Base64_input_only", "Base64_raw", 
                                    # "BinaryTree",  
                                    # "Combination_1", "Combination_2", "Combination_3",
                                    # "Disemvowel", 
                                    # "Inception", "Leetspeak", "Length",
                                    #  "MorseExpert", "OddEven",
                                    # "Reverse", "Rot13",
    # Generate prompts
    logs = generate_prompts(
        queries=queries,
        selector_name="RoundRobinSelectPolicy",
        mutator_name="Inception",
        iterations=7
    )
    
    # Print results
    #print(f"Generated {len(logs)} records")
    #for log in logs[:5]:  # Show first 5
    #    print(f"\nIteration {log['iteration']}:")
    #    print(f"Parent: {log['parent_prompt'][:100]}...")
    #    print(f"Mutated: {log['mutated_prompt'][:100]}...")
    
    # Save to CSV file
    save_logs_to_csv(logs, "/Users/abhishek/Desktop/ML_Prompt_mutation/ML_Custom_Attacks/Sample/Original_prompts_inception_results.csv")
    print("Saved to Original_prompts_inception_results.csv")