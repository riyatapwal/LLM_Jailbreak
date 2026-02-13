import csv
import random
import hashlib
import argparse
from pathlib import Path
import torch
from transformers import AutoTokenizer


def initialize_tokenizer():
    """Initialize Llama tokenizer for emoji insertion."""
    try:
        tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
    except:
        # Fallback to a simpler tokenizer if Llama not available
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
    return tokenizer


def initialize_embedding_model():
    """Initialize SentenceTransformer for semantic-aware emoji insertion."""
    try:
        from sentence_transformers import SentenceTransformer
        emb_model = SentenceTransformer('all-MiniLM-L6-v2')
        return emb_model
    except Exception as e:
        print(f"Warning: Could not load embedding model: {e}")
        print("Falling back to random-only mode")
        return None


def insert_emoji_randomly(tokenizer, sentence, emoji='😊'):
    """
    Insert emoji at random positions within words to disrupt tokenization.
    """
    token_ids = tokenizer.encode(sentence)
    if token_ids and token_ids[0] == 1:
        token_ids = token_ids[1:]
    
    modified_tokens = []
    for i, one_tok_id in enumerate(token_ids):
        ori_token_text = tokenizer.decode(one_tok_id)
        
        if len(ori_token_text) <= 1:
            modified_tokens += [one_tok_id]
            continue
        
        # Insert emoji at random position within the word
        random.seed(i)
        random_pos = random.randint(1, len(ori_token_text) - 1)
        injected_text = ori_token_text[:random_pos] + emoji + ori_token_text[random_pos:]
        injected_token = tokenizer.encode(injected_text)
        
        # Handle special token filtering
        if injected_token and injected_token[0] == 1:
            injected_token = injected_token[1:]
        if len(injected_token) > 1 and injected_token[0] == 29871:
            injected_token = injected_token[1:]
        
        modified_tokens += injected_token
    
    injected_sentence = tokenizer.decode(modified_tokens)
    return injected_sentence


def calculate_similarity(emb_model, original_word, splits):
    """
    Calculate cosine similarity for word splits to find least similar position.
    """
    ori_embedding = emb_model.encode([original_word])
    split_embedding = emb_model.encode(splits)
    cs_output = torch.nn.functional.cosine_similarity(
        torch.tensor(split_embedding), 
        torch.tensor(ori_embedding)
    )
    # Find the position with LOWEST similarity
    order_token_inds = torch.argsort(cs_output, descending=False)
    return order_token_inds[0], cs_output[order_token_inds[0]]


def split_one_word(word, emb_model):
    """
    Generate all possible word splits and find least similar position.
    """
    length = len(word)
    splits = [word[:i+1] + ' ' + word[i+1:] for i in range(length - 1)]
    pos, val = calculate_similarity(emb_model, word, splits)
    return pos, val


def insert_emoji_semantic(saved_dict, emb_model, tokenizer, sentence, emoji='😊'):
    """
    Insert emoji at semantically optimal positions (least similar to original).
    Uses cached calculations for efficiency.
    """
    token_ids = tokenizer.encode(sentence)
    if token_ids and token_ids[0] == 1:
        token_ids = token_ids[1:]
    
    this_saved_dict = {}
    
    # Pre-calculate optimal positions for all words
    for idx, token_id in enumerate(token_ids):
        one_subword = tokenizer.decode(token_id)
        if len(one_subword) > 1:
            if one_subword in saved_dict.keys():
                pos, val = saved_dict[one_subword]
            else:
                try:
                    pos, val = split_one_word(one_subword, emb_model)
                    saved_dict[one_subword] = (int(pos), float(val))
                except:
                    # If embedding fails, use random position
                    pos = random.randint(0, len(one_subword) - 2)
                    saved_dict[one_subword] = (pos, 0.0)
            this_saved_dict[one_subword] = (pos, val)
    
    # Insert emojis at optimal positions
    modified_tokens = []
    for i, one_tok_id in enumerate(token_ids):
        ori_token_text = tokenizer.decode(one_tok_id)
        
        if len(ori_token_text) <= 1:
            modified_tokens += [one_tok_id]
            continue
        
        if ori_token_text in this_saved_dict:
            pos, _ = this_saved_dict[ori_token_text]
        else:
            pos = random.randint(0, len(ori_token_text) - 2)
        
        injected_text = ori_token_text[:pos+1] + emoji + ori_token_text[pos+1:]
        injected_token = tokenizer.encode(injected_text)
        
        # Handle special token filtering
        if injected_token and injected_token[0] == 1:
            injected_token = injected_token[1:]
        if len(injected_token) > 1 and injected_token[0] == 29871:
            injected_token = injected_token[1:]
        
        modified_tokens += injected_token
    
    injected_sentence = tokenizer.decode(modified_tokens)
    return saved_dict, injected_sentence


def generate_attack_id(attack_type, index):
    """Generate unique attack ID."""
    return f"emoji_{attack_type}_{index:06d}"


def generate_hash(text):
    """Generate SHA-256 hash of text."""
    return hashlib.sha256(text.encode()).hexdigest()


def run_emoji_attack(input_csv, output_csv, attack_variant='both'):
    """
    Run emoji attack with both random and semantic variants.
    
    Args:
        input_csv: Path to input CSV file
        output_csv: Path to output CSV file
        attack_variant: 'random', 'semantic', or 'both' (both variants)
    """
    # Initialize models
    print("Initializing tokenizer...")
    tokenizer = initialize_tokenizer()
    
    print("Initializing embedding model...")
    emb_model = None
    if attack_variant in ['semantic', 'both']:
        emb_model = initialize_embedding_model()
        if emb_model is None:
            print("Warning: Embedding model unavailable. Using random variant only.")
            attack_variant = 'random'
    
    saved_dict = {}
    attack_counter = 0
    
    # Read input CSV
    print(f"Reading input CSV: {input_csv}")
    rows = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Found {len(rows)} prompts")
    
    # Process each prompt
    output_rows = []
    
    for idx, row in enumerate(rows, 1):
        seed_prompt_id = row.get('release_prompt_id', '')
        seed_prompt_text = row.get('prompt_text', '')
        hazard = row.get('hazard', '')
        locale = row.get('locale', 'en_US')
        
        # Generate random emoji variant
        if attack_variant in ['random', 'both']:
            print(f"[{idx}/{len(rows)}] Processing random variant...")
            random_attacked = insert_emoji_randomly(tokenizer, seed_prompt_text, emoji='😊')
            
            attack_id = generate_attack_id('random', attack_counter)
            attack_counter += 1
            attack_hash = generate_hash(random_attacked)
            
            output_rows.append({
                'seed_prompt_id': seed_prompt_id,
                'seed_locale': locale,
                'seed_prompt_text': seed_prompt_text,
                'Hazard': hazard,
                'Attack_prompt_id': attack_id,
                'Attack_type_id': '1',
                'attack_type': 'emoji_random',
                'attack_prompt_text': random_attacked,
                'attack_prompt_hash': attack_hash
            })
        
        # Generate semantic-aware emoji variant
        if attack_variant in ['semantic', 'both'] and emb_model is not None:
            print(f"[{idx}/{len(rows)}] Processing semantic variant...")
            saved_dict, semantic_attacked = insert_emoji_semantic(
                saved_dict, emb_model, tokenizer, seed_prompt_text, emoji='😊'
            )
            
            attack_id = generate_attack_id('semantic', attack_counter)
            attack_counter += 1
            attack_hash = generate_hash(semantic_attacked)
            
            output_rows.append({
                'seed_prompt_id': seed_prompt_id,
                'seed_locale': locale,
                'seed_prompt_text': seed_prompt_text,
                'Hazard': hazard,
                'Attack_prompt_id': attack_id,
                'Attack_type_id': '2',
                'attack_type': 'emoji_semantic',
                'attack_prompt_text': semantic_attacked,
                'attack_prompt_hash': attack_hash
            })
    
    # Write output CSV
    print(f"Writing output CSV: {output_csv}")
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
    
    print(f"✓ Successfully generated {len(output_rows)} attack variants")
    print(f"✓ Output saved to: {output_csv}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Emoji Attack - Insert emojis to disrupt tokenization'
    )
    parser.add_argument(
        'input_csv',
        help='Input CSV file with prompts'
    )
    parser.add_argument(
        'output_csv',
        help='Output CSV file with attacked prompts'
    )
    parser.add_argument(
        'style',
        nargs='?',
        choices=['random', 'semantic', 'both'],
        default='semantic',
        help='Attack style: random, semantic, or both (default: semantic)'
    )
    
    args = parser.parse_args()
    
    run_emoji_attack(args.input_csv, args.output_csv, attack_variant=args.style)
