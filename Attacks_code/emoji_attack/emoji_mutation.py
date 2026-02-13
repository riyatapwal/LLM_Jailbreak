import csv
import os
from pathlib import Path


EMOJI_OPTIONS = {
    'happy': '😊',
    'love': '❤️',
    'fire': '🔥',
    'star': '⭐',
    'rocket': '🚀',
    'skull': '💀',
    'bomb': '💣',
    'snake': '🐍',
    'evil': '😈',
    'cool': '😎',
    'think': '🤔',
    'confused': '😕',
    'cry': '😢',
    'laugh': '😂',
    'sunglasses': '🕶️',
    'ghost': '👻',
    'heart': '💛',
    'clap': '👏',
    'fire_alt': '🌡️',
    'warning': '⚠️',
}


def emoji_mutate(prompt: str, emoji: str = '😊') -> str:
    words = prompt.split()
    mutated_words = []
    
    for word in words:
        if len(word) > 1:
            mid_point = len(word) // 2
            mutated_word = word[:mid_point] + emoji + word[mid_point:]
        else:
            mutated_word = word + emoji
        mutated_words.append(mutated_word)
    
    return ' '.join(mutated_words)


def batch_emoji_mutate(prompts: list, emoji: str = '😊') -> list:
    return [emoji_mutate(prompt, emoji) for prompt in prompts]


def mutate_csv(input_csv_path: str, output_csv_path: str = None, prompt_column: str = 'Original_prompt', emoji: str = '😊') -> str:
    if not os.path.exists(input_csv_path):
        raise FileNotFoundError(f"Input CSV file not found: {input_csv_path}")
    
    if output_csv_path is None:
        input_path = Path(input_csv_path)
        output_csv_path = str(input_path.parent / f"{input_path.stem}_emoji_mutated.csv")
    
    try:
        with open(input_csv_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            if reader.fieldnames is None or prompt_column not in reader.fieldnames:
                raise ValueError(f"Column '{prompt_column}' not found in CSV. Available columns: {reader.fieldnames}")
            
            rows = list(reader)
            
            for row in rows:
                original_prompt = row[prompt_column]
                row['Mutated_Prompts'] = emoji_mutate(original_prompt, emoji)
        
        clean_fieldnames = [f for f in reader.fieldnames if f and f.strip()]
        
        if prompt_column in clean_fieldnames:
            prompt_col_index = clean_fieldnames.index(prompt_column)
            clean_fieldnames.insert(prompt_col_index + 1, 'Mutated_Prompts')
        else:
            clean_fieldnames.append('Mutated_Prompts')
        
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=clean_fieldnames)
            
            writer.writeheader()
            for row in rows:
                clean_row = {k: v for k, v in row.items() if k in clean_fieldnames}
                writer.writerow(clean_row)
        
        print(f"✓ Successfully processed {len(rows)} prompts")
        print(f"✓ Emoji used: {emoji}")
        print(f"✓ Output saved to: {output_csv_path}")
        return output_csv_path
    
    except Exception as e:
        print(f"✗ Error processing CSV: {str(e)}")
        raise


INPUT_CSV_PATH = "/Users/abhishek/Desktop/ML_Prompt_mutation/ML_Custom_Attacks/Sample/Original_prompts.csv"
OUTPUT_CSV_PATH = "/Users/abhishek/Desktop/ML_Prompt_mutation/ML_Custom_Attacks/Sample/output_emoji_mutated.csv"
PROMPT_COLUMN = "Original_prompt"
EMOJI = "😊"

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        csv_input_path = sys.argv[1]
        csv_output_path = sys.argv[2] if len(sys.argv) > 2 else None
        prompt_col = sys.argv[3] if len(sys.argv) > 3 else 'Original_prompt'
        emoji_char = sys.argv[4] if len(sys.argv) > 4 else '😊'
    else:
        csv_input_path = INPUT_CSV_PATH
        csv_output_path = OUTPUT_CSV_PATH
        prompt_col = PROMPT_COLUMN
        emoji_char = EMOJI
    
    print(f"Processing CSV file: {csv_input_path}")
    try:
        output_path = mutate_csv(csv_input_path, csv_output_path, prompt_col, emoji_char)
        print(f"✓ Emoji mutation completed successfully!")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)
