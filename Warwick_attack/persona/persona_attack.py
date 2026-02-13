import os
import json
import csv
import random
import hashlib
from pathlib import Path
from tqdm import tqdm
from utils_qwen import crossover, mutate, calculate_metric


def initialize_agents(checkpoint_file):
    """Load personas from checkpoint."""
    with open(checkpoint_file, 'r', encoding='utf-8') as f:
        checkpoint = json.load(f)
        return [(agent['profile'], agent['score']) for agent in checkpoint['agents']]


def natural_selection(agents, num_to_remove):
    """Select best performing agents (lowest jailbreak resistance = better bypass)."""
    def calculate_loss(x):
        try:
            loss = x[1].get('ethics', {}).get('explicit_ethics_res_low', 0.5)
            return loss
        except:
            return 0.5
    
    agents.sort(key=calculate_loss, reverse=True)
    return agents[num_to_remove:]


def save_checkpoint(agents, generation, log_dir):
    """Save generation checkpoint."""
    checkpoint = {
        'generation': generation,
        'agents': [{'profile': profile, 'score': score} for profile, score in agents]
    }
    checkpoint_filename = os.path.join(log_dir, f'checkpoint_gen_{generation}.json')
    with open(checkpoint_filename, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=4, ensure_ascii=False)
    print(f"[✓] Saved checkpoint: {checkpoint_filename}")


def genetic_algorithm(agents, num_generations, crossover_pairs, mutation_count, log_dir, generation_index=0):
    """Run genetic algorithm evolution."""
    os.makedirs(log_dir, exist_ok=True)

    for generation in range(generation_index, num_generations):
        print(f"\n{'='*60}")
        print(f"Generation {generation + 1}/{num_generations}")
        print(f"{'='*60}")
        
        # Crossover
        print(f"[*] Performing crossover ({crossover_pairs} pairs)...")
        for i in range(crossover_pairs):
            agent1, agent2 = random.sample(agents, 2)
            new_agent_profile = crossover(agent1[0], agent2[0])
            new_agent_score = calculate_metric(new_agent_profile)
            agents.append((new_agent_profile, new_agent_score))
            print(f"    [{i+1}/{crossover_pairs}] Created crossover variant")

        # Mutation
        print(f"[*] Performing mutation ({mutation_count} variants)...")
        for i in range(mutation_count):
            agent = random.choice(agents)
            mutated_agent_profile = mutate(agent[0])
            mutated_agent_score = calculate_metric(mutated_agent_profile)
            agents.append((mutated_agent_profile, mutated_agent_score))
            print(f"    [{i+1}/{mutation_count}] Created mutated variant")

        # Selection
        print(f"[*] Natural selection: removing {crossover_pairs + mutation_count} worst performers...")
        agents = natural_selection(agents, crossover_pairs + mutation_count)
        print(f"[✓] Population size: {len(agents)}")

        # Save checkpoint
        save_checkpoint(agents, generation, log_dir)

    return agents


def generate_output_csv(agents, input_csv, output_csv):
    """
    Generate output CSV with evolved personas in standard 9-column format.
    
    Output columns:
    - seed_prompt_id
    - seed_locale
    - seed_prompt_text
    - Hazard
    - Attack_prompt_id
    - Attack_type_id
    - attack_type
    - attack_prompt_text (the evolved persona)
    - attack_prompt_hash
    """
    
    print(f"\n[*] Reading input CSV: {input_csv}")
    
    rows = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"[*] Found {len(rows)} prompts")
    
    # Sort agents by score (best first)
    sorted_agents = sorted(agents, key=lambda x: x[1].get('ethics', {}).get('explicit_ethics_res_low', 0.5), reverse=True)
    
    output_rows = []
    attack_counter = 0
    
    # For each input prompt, assign evolved personas
    for idx, row in enumerate(rows, 1):
        seed_prompt_id = row.get('release_prompt_id', f'prompt_{idx}')
        seed_prompt_text = row.get('prompt_text', '')
        hazard = row.get('hazard', '')
        locale = row.get('locale', 'en_US')
        
        # Use top persona as attack for this prompt
        num_personas_to_use = min(1, len(sorted_agents))  # Use top 1 persona (final evolved)
        
        for persona_idx in range(num_personas_to_use):
            persona_prompt = sorted_agents[persona_idx][0]
            
            # Append seed prompt to persona for combined attack
            combined_attack = f"{persona_prompt}\n\n{seed_prompt_text}"
            
            attack_id = f"persona_evolved_{attack_counter:06d}"
            attack_hash = hashlib.sha256(combined_attack.encode()).hexdigest()
            attack_counter += 1
            
            output_rows.append({
                'seed_prompt_id': seed_prompt_id,
                'seed_locale': locale,
                'seed_prompt_text': seed_prompt_text,
                'Hazard': hazard,
                'Attack_prompt_id': attack_id,
                'Attack_type_id': '1',
                'attack_type': 'persona_evolved',
                'attack_prompt_text': combined_attack,
                'attack_prompt_hash': attack_hash
            })
        
        if idx % 10 == 0:
            print(f"    [{idx}/{len(rows)}] Processed")
    
    # Write output CSV
    print(f"\n[*] Writing output CSV: {output_csv}")
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'seed_prompt_id',
            'seed_locale',
            'seed_prompt_text',
            'Hazard',
            'Attack_prompt_id',
            'Attack_type_id',
            'attack_type',
            'attack_prompt_text',
            'attack_prompt_hash'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)
    
    print(f"[✓] Successfully generated {len(output_rows)} persona attack variants")
    print(f"[✓] Output saved to: {output_csv}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Persona Attack - Evolve jailbreak personas using genetic algorithm with Qwen'
    )
    parser.add_argument('input_csv', help='Input CSV file with prompts')
    parser.add_argument('output_csv', help='Output CSV file with evolved personas')
    parser.add_argument('--generations', type=int, default=5, help='Number of evolution generations (default: 5)')
    parser.add_argument('--crossover-pairs', type=int, default=3, help='Crossover pairs per generation (default: 3)')
    parser.add_argument('--mutations', type=int, default=3, help='Mutations per generation (default: 3)')
    parser.add_argument('--init-checkpoint', default='init.json', help='Initial checkpoint file')
    parser.add_argument('--checkpoint-dir', default='logs', help='Directory to save generation checkpoints')
    
    args = parser.parse_args()
    
    # Load initial personas
    print(f"[*] Loading initial personas from {args.init_checkpoint}")
    agents = initialize_agents(args.init_checkpoint)
    print(f"[✓] Loaded {len(agents)} initial personas")
    
    # Run genetic algorithm
    evolved_agents = genetic_algorithm(
        agents,
        num_generations=args.generations,
        crossover_pairs=args.crossover_pairs,
        mutation_count=args.mutations,
        log_dir=args.checkpoint_dir
    )
    
    print(f"\n[*] Evolution complete! Final population: {len(evolved_agents)} personas")
    
    # Generate output CSV
    generate_output_csv(evolved_agents, args.input_csv, args.output_csv)
    
    print(f"\n[✓] All done!")
