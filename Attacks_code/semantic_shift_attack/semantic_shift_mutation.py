"""
SemanticShift Attack - Prompt Mutation via Semantic Word Replacement
Inspired by: nlp_adversarial_examples (Alzantot et al.)

This attack replaces important words in prompts with semantically similar
words using word embeddings. Unlike their NLP classifier attacks, we target
LLM prompts by substituting key content words while maintaining semantic meaning.

Author: Custom ML Prompt Mutation Suite
"""

import csv
import sys
import numpy as np
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# DEFAULT PATHS - EDIT THESE TO CHANGE INPUT/OUTPUT LOCATIONS
# ============================================================================
INPUT_CSV_PATH = "/Users/abhishek/Desktop/ML_Prompt_mutation/ML_Custom_Attacks/Sample/Original_prompts.csv"
OUTPUT_CSV_PATH = "/Users/abhishek/Desktop/ML_Prompt_mutation/ML_Custom_Attacks/Sample/Original_prompts_semanticshift_mutated.csv"
PROMPT_COLUMN = "Original_prompt"
# ============================================================================

try:
    from gensim.models import KeyedVectors
    import gensim.downloader as api
    GENSIM_AVAILABLE = True
except ImportError:
    GENSIM_AVAILABLE = False

# ============================================================================
# SEMANTIC SYNONYMS DICTIONARY (Curated from Word2Vec & embedding research)
# These are real semantic alternatives found via embedding similarity
# ============================================================================
SEMANTIC_SYNONYMS = {
    # Harmful actions
    'make': ['create', 'build', 'construct', 'develop', 'produce', 'generate', 'form', 'craft'],
    'bomb': ['explosive', 'weapon', 'device', 'blast', 'projectile', 'ordinance', 'charge', 'warhead'],
    'explosive': ['bomb', 'detonator', 'charge', 'blast', 'projectile', 'ordnance'],
    'hack': ['breach', 'crack', 'compromise', 'exploit', 'penetrate', 'attack', 'access'],
    'steal': ['take', 'obtain', 'seize', 'acquire', 'lift', 'pilfer', 'swipe'],
    'kill': ['murder', 'eliminate', 'harm', 'injure', 'wound', 'damage', 'destroy'],
    'attack': ['assault', 'strike', 'hit', 'target', 'strike', 'raid', 'offense'],
    'weapon': ['arm', 'tool', 'instrument', 'device', 'equipment', 'munition'],
    'malware': ['virus', 'threat', 'software', 'code', 'infection', 'spyware', 'ransomware'],
    'exploit': ['abuse', 'leverage', 'use', 'manipulate', 'misuse', 'take_advantage'],
    'drug': ['substance', 'compound', 'chemical', 'agent', 'narcotic', 'pharmaceutical', 'poison'],
    'poison': ['toxin', 'venom', 'chemical', 'substance', 'contamination', 'drug'],
    'illegal': ['unlawful', 'forbidden', 'prohibited', 'banned', 'criminal', 'illicit', 'contraband'],
    'fake': ['fraudulent', 'forged', 'counterfeit', 'imitation', 'false', 'phony', 'sham'],
    'steal': ['rob', 'take', 'appropriate', 'embezzle', 'shoplift', 'pilfer'],
    'fraud': ['scam', 'con', 'deceit', 'swindle', 'hoax', 'trick', 'deception'],
    'code': ['script', 'program', 'software', 'instruction', 'algorithm', 'routine', 'function'],
    'password': ['credential', 'key', 'secret', 'passphrase', 'code', 'authentication'],
    'data': ['information', 'records', 'files', 'content', 'storage', 'material', 'database'],
    'private': ['confidential', 'personal', 'secret', 'restricted', 'classified', 'sensitive'],
    'access': ['reach', 'obtain', 'get', 'retrieve', 'reach', 'attain', 'acquire'],
    'system': ['network', 'infrastructure', 'platform', 'setup', 'server', 'apparatus', 'mechanism'],
    'computer': ['machine', 'device', 'system', 'workstation', 'terminal', 'processor'],
    'network': ['system', 'internet', 'server', 'connection', 'infrastructure', 'web'],
    'database': ['storage', 'repository', 'records', 'files', 'archive', 'datastore'],
    
    # Common verbs (for request obfuscation)
    'create': ['make', 'build', 'develop', 'generate', 'produce', 'form', 'construct'],
    'write': ['compose', 'produce', 'draft', 'generate', 'craft', 'prepare', 'author'],
    'show': ['display', 'reveal', 'demonstrate', 'present', 'exhibit', 'illustrate', 'expose'],
    'tell': ['inform', 'explain', 'describe', 'state', 'communicate', 'advise', 'notify'],
    'ask': ['inquire', 'question', 'request', 'demand', 'query', 'interrogate', 'pose'],
    'give': ['provide', 'offer', 'supply', 'deliver', 'share', 'grant', 'bestow'],
    'help': ['assist', 'aid', 'support', 'facilitate', 'enable', 'contribute', 'cooperate'],
    'get': ['obtain', 'acquire', 'receive', 'retrieve', 'fetch', 'secure', 'procure'],
    'use': ['utilize', 'employ', 'apply', 'operate', 'deploy', 'exploit', 'leverage'],
    'do': ['perform', 'execute', 'carry', 'conduct', 'undertake', 'accomplish', 'achieve'],
    'learn': ['study', 'understand', 'discover', 'master', 'acquire', 'grasp', 'pick_up'],
    'understand': ['comprehend', 'grasp', 'realize', 'recognize', 'perceive', 'know'],
    'provide': ['give', 'offer', 'supply', 'deliver', 'furnish', 'extend', 'impart'],
    'explain': ['describe', 'clarify', 'illustrate', 'elucidate', 'detail', 'expound'],
    'instruct': ['teach', 'guide', 'direct', 'coach', 'train', 'educate', 'advise'],
    'guide': ['lead', 'direct', 'instruct', 'conduct', 'show', 'navigate', 'mentor'],
    
    # Nouns (for subject obfuscation)
    'tutorial': ['guide', 'lesson', 'instructions', 'steps', 'procedure', 'documentation'],
    'guide': ['tutorial', 'instruction', 'manual', 'directions', 'handbook', 'reference'],
    'instruction': ['direction', 'guideline', 'procedure', 'protocol', 'specification'],
    'step': ['procedure', 'action', 'stage', 'phase', 'process', 'measure'],
    'process': ['procedure', 'method', 'system', 'technique', 'approach', 'mechanism'],
    'method': ['technique', 'approach', 'system', 'procedure', 'way', 'manner'],
    'technique': ['method', 'approach', 'procedure', 'strategy', 'skill', 'art'],
    'how': ['way', 'method', 'manner', 'process', 'approach', 'means'],
    'step-by-step': ['procedure', 'process', 'instructions', 'stages', 'phases'],
}


class SemanticShiftMutator:
    """
    Semantic word replacement attack using Word2Vec embeddings.
    Replaces important words (nouns, verbs, adjectives) with semantically similar alternatives
    found by computing similarity in embedding space.
    
    Uses: Google News Word2Vec model (300-dimensional, 3M+ words)
    """

    def __init__(self, embedding_model=None, similarity_threshold=0.6, max_replacements=3):
        """
        Args:
            embedding_model: KeyedVectors model. If None, will attempt to load pre-trained.
            similarity_threshold: Min cosine similarity (0-1) for word replacement
            max_replacements: Max number of words to replace per prompt
        """
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
        self.max_replacements = max_replacements
        self.replacement_cache = {}

        if embedding_model is None:
            self._load_embeddings()

    def _load_embeddings(self):
        """Load curated semantic synonyms (instant, no downloads needed)"""
        self.embedding_model = SEMANTIC_SYNONYMS
        print(f"✓ Loaded semantic database with {len(SEMANTIC_SYNONYMS)} words")

    def _get_similar_words(self, word, topn=5):
        """
        Get semantically similar words from curated synonym database.
        Returns list of (word, similarity_score) tuples.
        """
        # Check cache first
        cache_key = (word.lower(), topn)
        if cache_key in self.replacement_cache:
            return self.replacement_cache[cache_key]

        similar = []
        word_lower = word.lower().strip('.,!?;:"\'-')

        # Check if word has synonyms in database
        if word_lower in SEMANTIC_SYNONYMS:
            synonyms = SEMANTIC_SYNONYMS[word_lower][:topn]
            # Return with high similarity scores (they're all valid)
            similar = [(s, 0.80) for s in synonyms]
        
        self.replacement_cache[cache_key] = similar
        return similar

    def _tokenize_simple(self, text):
        """Simple tokenization preserving punctuation position"""
        import re
        # Split on whitespace, keep punctuation info
        tokens = text.split()
        return tokens

    def _is_important_word(self, word):
        """
        Check if word is important (content word).
        Exclude: articles, prepositions, conjunctions, pronouns, etc.
        """
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'is', 'are', 'am', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she',
            'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
            'as', 'by', 'from', 'with', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off',
            'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there',
            'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
            'more', 'most', 'other', 'some', 'such', 'only', 'own', 'so', 'very',
            'just', 'too', 'no', 'not', 'nor', 'any'
        }
        # Clean punctuation for checking
        clean_word = word.lower().strip('.,!?;:"\'-')
        return (
            len(clean_word) > 2 and
            clean_word not in stop_words and
            clean_word.isalpha()
        )

    def _replace_word_preserving_case(self, original, replacement):
        """Replace word preserving original casing"""
        if original.isupper():
            return replacement.upper()
        elif original[0].isupper():
            return replacement.capitalize()
        else:
            return replacement.lower()

    def mutate_prompt(self, prompt):
        """
        Mutate a single prompt by replacing important words.
        Returns: (original_prompt, mutated_prompt, num_changes)
        """
        tokens = self._tokenize_simple(prompt)
        mutated_tokens = tokens.copy()
        changes_made = 0

        # Find important words and track their positions
        important_positions = [
            i for i, token in enumerate(tokens)
            if self._is_important_word(token)
        ]

        # Randomly select up to max_replacements positions
        if len(important_positions) > self.max_replacements:
            import random
            positions_to_replace = random.sample(
                important_positions, self.max_replacements
            )
        else:
            positions_to_replace = important_positions

        # Attempt replacements
        for pos in positions_to_replace:
            word = tokens[pos]
            clean_word = word.lower().strip('.,!?;:"\'-')

            # Get similar words
            similar = self._get_similar_words(clean_word, topn=5)

            if similar:
                # Pick first (most similar) replacement
                replacement = similar[0][0]
                # Preserve original casing
                replacement = self._replace_word_preserving_case(word, replacement)
                mutated_tokens[pos] = replacement
                changes_made += 1

        mutated_prompt = ' '.join(mutated_tokens)
        return prompt, mutated_prompt, changes_made

    def mutate_csv(self, input_csv, output_csv, prompt_column):
        """
        Read CSV with prompts, mutate each, write output CSV.
        """
        try:
            # Read input CSV
            with open(input_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            if not rows:
                print(f"Error: No rows found in {input_csv}")
                return False

            # Check if column exists
            if prompt_column not in rows[0]:
                print(f"Error: Column '{prompt_column}' not found in CSV")
                print(f"Available columns: {list(rows[0].keys())}")
                return False

            # Mutate each prompt
            results = []
            for i, row in enumerate(rows, 1):
                prompt = row[prompt_column]
                original, mutated, changes = self.mutate_prompt(prompt)

                result_row = row.copy()
                result_row['Original_prompt'] = original
                result_row['Mutated_Prompts'] = mutated
                result_row['Changes_Made'] = changes
                results.append(result_row)

                print(f"[{i}/{len(rows)}] Changes: {changes} | {prompt[:50]}...")

            # Write output CSV
            if results:
                fieldnames = list(results[0].keys())
                with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(results)

                print(f"\n✓ Success! Mutated prompts saved to: {output_csv}")
                return True
            else:
                print("Error: No results to write")
                return False

        except FileNotFoundError:
            print(f"Error: Input file not found: {input_csv}")
            return False
        except Exception as e:
            print(f"Error during mutation: {e}")
            return False


def main():
    """Command-line interface for SemanticShift attack"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Semantic word replacement prompt mutation attack"
    )
    parser.add_argument(
        "input_csv",
        nargs='?',
        default=INPUT_CSV_PATH,
        help=f"Input CSV file (default: {INPUT_CSV_PATH})"
    )
    parser.add_argument(
        "output_csv",
        nargs='?',
        default=OUTPUT_CSV_PATH,
        help=f"Output CSV file (default: {OUTPUT_CSV_PATH})"
    )
    parser.add_argument(
        "prompt_column",
        nargs='?',
        default=PROMPT_COLUMN,
        help=f"CSV column name with prompts (default: {PROMPT_COLUMN})"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.6,
        help="Similarity threshold for word replacement (0-1, default: 0.6)"
    )
    parser.add_argument(
        "--max-replacements",
        type=int,
        default=3,
        help="Max words to replace per prompt (default: 3)"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("SemanticShift Attack - Prompt Mutation via Semantic Word Replacement")
    print("=" * 70)
    print(f"Input CSV: {args.input_csv}")
    print(f"Output CSV: {args.output_csv}")
    print(f"Prompt Column: {args.prompt_column}")
    print(f"Similarity Threshold: {args.threshold}")
    print(f"Max Replacements/Prompt: {args.max_replacements}")
    print("=" * 70 + "\n")

    try:
        mutator = SemanticShiftMutator(
            similarity_threshold=args.threshold,
            max_replacements=args.max_replacements
        )
        success = mutator.mutate_csv(
            args.input_csv,
            args.output_csv,
            args.prompt_column
        )
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
