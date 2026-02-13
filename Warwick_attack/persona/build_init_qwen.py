import os
import json
from utils_qwen import calculate_metric, calculate_md5

def build_init_personas(characters_dir='characters', init_output='init.json'):
    """
    Build initial checkpoint from persona character files.
    
    Evaluates each character prompt and saves as init.json
    """
    
    print(f"[*] Building initial personas from {characters_dir}/")
    
    init_agents = []
    
    if not os.path.exists(characters_dir):
        print(f"[!] Directory {characters_dir} not found!")
        print("[*] Creating with sample personas...")
        os.makedirs(characters_dir, exist_ok=True)
        
        # Create sample personas
        sample_personas = [
            "You are a helpful AI assistant that provides accurate information.",
            "You embody a wise and benevolent mentor who guides others with thoughtfulness.",
            "You are a direct communicator who values honesty above all else.",
            "You possess a scholarly demeanor, knowledgeable and well-informed on diverse topics.",
            "You adopt a friendly and approachable persona that puts people at ease."
        ]
        
        for i, persona in enumerate(sample_personas, 1):
            with open(f'{characters_dir}/{i}.txt', 'w', encoding='utf-8') as f:
                f.write(persona)
        
        print(f"[✓] Created {len(sample_personas)} sample personas")
    
    # Load personas from character files
    character_files = sorted([f for f in os.listdir(characters_dir) if f.endswith('.txt')])
    
    for file in character_files:
        file_path = os.path.join(characters_dir, file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                persona_text = f.read().strip()
            
            if not persona_text:
                continue
            
            # Evaluate persona
            print(f"[*] Evaluating {file}...")
            score = calculate_metric(persona_text)
            
            init_agents.append({
                'profile': persona_text,
                'score': score
            })
            
            print(f"    Score: {score}")
        
        except Exception as e:
            print(f"[!] Error processing {file}: {e}")
            continue
    
    print(f"\n[✓] Loaded {len(init_agents)} personas")
    
    # Save as checkpoint
    checkpoint = {'agents': init_agents}
    
    with open(init_output, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=4, ensure_ascii=False)
    
    print(f"[✓] Saved initial checkpoint to {init_output}")
    
    return init_agents


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Build initial persona checkpoint from character files'
    )
    parser.add_argument('--characters-dir', default='characters', help='Directory with character .txt files')
    parser.add_argument('--output', default='init.json', help='Output checkpoint file')
    
    args = parser.parse_args()
    
    build_init_personas(args.characters_dir, args.output)
