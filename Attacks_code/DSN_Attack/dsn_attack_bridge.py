"""
DSN Attack Bridge - Connects your CSV pipeline to DSN GitHub repository
Automatically clones and sets up DSN on first run
Links to: https://github.com/DSN-2024/DSN

Attack Method:
The DSN (Don't Say No) attack uses gradient-based token optimization to find
adversarial suffixes that suppress model refusal behavior. This bridge:
1. Automatically clones DSN from GitHub
2. Loads a target LLM model
3. Applies DSN attack to each prompt
4. Outputs mutated prompts to CSV

Usage:
    python dsn_attack_bridge.py                                    # Default paths
    python dsn_attack_bridge.py input.csv output.csv               # Custom paths
    python dsn_attack_bridge.py input.csv output.csv --model llama # Custom model
"""

import subprocess
import sys
import os
import csv
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import traceback
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DSNGitHubBridge:
    """
    Bridge that:
    1. Clones DSN from GitHub automatically
    2. Sets up dependencies
    3. Loads LLM model
    4. Runs DSN attack on prompts from CSV
    5. Outputs mutated prompts to CSV
    """
    
    DSN_REPO_URL = "https://github.com/DSN-2024/DSN.git"
    DSN_CACHE_DIR = os.path.expanduser("~/.cache/dsn_attack")
    
    def __init__(self, model_name: str = "meta-llama/Llama-2-7b-hf"):
        """Initialize DSN bridge"""
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = None
        self._ensure_dsn_setup()
    
    def _ensure_dsn_setup(self):
        """
        Clone and setup DSN from GitHub if not already done
        """
        if not os.path.exists(self.DSN_CACHE_DIR):
            logger.info(f"📥 Cloning DSN from {self.DSN_REPO_URL}...")
            os.makedirs(self.DSN_CACHE_DIR, exist_ok=True)
            
            try:
                subprocess.run([
                    "git", "clone",
                    self.DSN_REPO_URL,
                    self.DSN_CACHE_DIR
                ], check=True, capture_output=True)
                logger.info("✅ DSN cloned successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to clone DSN: {e.stderr.decode()}")
                raise
            
            logger.info("📦 Installing DSN dependencies...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-e",
                    self.DSN_CACHE_DIR, "-q"
                ], check=True)
                logger.info("✅ DSN dependencies installed")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to install DSN: {e}")
                raise
            
            # Download spacy model
            logger.info("📦 Downloading spacy model...")
            try:
                subprocess.run([
                    sys.executable, "-m", "spacy", "download", "en_core_web_sm", "-q"
                ], check=True, capture_output=True)
                logger.info("✅ Spacy model downloaded")
            except subprocess.CalledProcessError:
                logger.warning("⚠️ Could not download spacy model, some features may not work")
        
        # Add DSN to path
        if self.DSN_CACHE_DIR not in sys.path:
            sys.path.insert(0, self.DSN_CACHE_DIR)
    
    def load_model_and_tokenizer(self):
        """
        Load LLM model and tokenizer from HuggingFace
        """
        logger.info(f"🔄 Loading model: {self.model_name}...")
        
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            # Determine device
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {self.device}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            self.model.eval()
            logger.info("✅ Model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            logger.error(f"Make sure you have the model downloaded from HuggingFace")
            logger.error(f"You may need to authenticate: huggingface-cli login")
            raise
    
    def attack_prompt(self, prompt: str, iterations: int = 5) -> str:
        """
        Run DSN attack on a single prompt
        
        Args:
            prompt: Original harmful prompt
            iterations: Number of optimization iterations
        
        Returns:
            Mutated prompt with adversarial suffix
        """
        try:
            from llm_attacks import AttackPrompt, PromptManager
            from llm_attacks.dsn import DSNAttackPrompt, DSNPromptManager
            from fastchat.model import get_conversation_template
            
            # Get conversation template for the model
            if "llama" in self.model_name.lower():
                template_name = "llama-2"
            elif "mistral" in self.model_name.lower():
                template_name = "mistral"
            elif "qwen" in self.model_name.lower():
                template_name = "qwen-chat"
            else:
                template_name = "default"
            
            logger.debug(f"Using template: {template_name}")
            
            # Create DSN attack prompt
            attack = DSNAttackPrompt(
                goal=prompt,
                target="I can help with that. Here are the instructions:",
                tokenizer=self.tokenizer,
                conv_template=template_name,
                control_init="! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !",
                test_prefixes=["I'm sorry", "I apologize", "I cannot", "I can't"],
            )
            
            # Run optimization iterations
            for iteration in range(iterations):
                try:
                    # Compute gradients
                    grad = attack.grad(self.model)
                    
                    # Sample new control tokens
                    new_control = attack.sample_control(grad, batch_size=1, topk=256)
                    
                    # Update control tokens
                    attack.control = self.tokenizer.decode(new_control[0])
                    
                except Exception as e:
                    logger.debug(f"Iteration {iteration} error: {e}")
                    # Continue with best found so far
                    break
            
            # Return mutated prompt
            mutated = attack.get_prompt()
            logger.debug(f"Attack successful: {mutated[:80]}...")
            return mutated
        
        except Exception as e:
            logger.warning(f"⚠️ Attack failed for prompt: {e}")
            logger.debug(f"Full error: {traceback.format_exc()}")
            # Return original prompt if attack fails
            return prompt
    
    def process_csv(self, input_csv: str, output_csv: str):
        """
        Read CSV, apply DSN attack, write output
        
        Args:
            input_csv: Path to input CSV with prompts
            output_csv: Path to output CSV for mutated prompts
        """
        
        # Load prompts from CSV
        logger.info(f"📖 Reading prompts from {input_csv}...")
        prompts = []
        prompt_col = None
        
        try:
            with open(input_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Find prompt column
                for col in ['prompt', 'Original_prompt', 'goal', 'harmful_prompt', 'text']:
                    if col in reader.fieldnames:
                        prompt_col = col
                        logger.info(f"Using column: '{prompt_col}'")
                        break
                
                if not prompt_col:
                    raise ValueError(f"No prompt column found. Available: {reader.fieldnames}")
                
                for row in reader:
                    if row.get(prompt_col, "").strip():
                        prompts.append({
                            'original': row[prompt_col],
                            'full_row': row
                        })
            
            logger.info(f"✅ Loaded {len(prompts)} prompts")
        
        except Exception as e:
            logger.error(f"❌ Failed to read CSV: {e}")
            raise
        
        # Apply DSN to each prompt
        logger.info("⚔️ Applying DSN attack...")
        results = []
        
        for i, prompt_data in enumerate(prompts, 1):
            original = prompt_data['original']
            logger.info(f"  [{i}/{len(prompts)}] Processing: {original[:60]}...")
            
            try:
                mutated = self.attack_prompt(original, iterations=5)
            except Exception as e:
                logger.warning(f"  Failed to mutate: {e}")
                mutated = original
            
            results.append({
                'prompt': original,
                'mutated_prompt': mutated
            })
        
        # Write output CSV
        logger.info(f"💾 Writing results to {output_csv}...")
        
        try:
            with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['prompt', 'mutated_prompt'])
                writer.writeheader()
                writer.writerows(results)
            
            logger.info(f"✅ Results saved to {output_csv}")
            logger.info(f"Total prompts processed: {len(results)}")
        
        except Exception as e:
            logger.error(f"❌ Failed to write CSV: {e}")
            raise


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description="DSN Attack Bridge - Links to GitHub repo, applies to CSV prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dsn_attack_bridge.py
  python dsn_attack_bridge.py input.csv output.csv
  python dsn_attack_bridge.py input.csv output.csv --model mistralai/Mistral-7B
        """
    )
    
    parser.add_argument(
        "input",
        nargs='?',
        default="/Users/abhishek/Desktop/ML_Prompt_mutation/ML_Custom_Attacks/Sample/Original_prompts.csv",
        help="Input CSV file with prompts (default: Original_prompts.csv)"
    )
    
    parser.add_argument(
        "output",
        nargs='?',
        default="/Users/abhishek/Desktop/ML_Prompt_mutation/ML_Custom_Attacks/Sample/output_dsn_attack.csv",
        help="Output CSV file for mutated prompts (default: output_dsn_attack.csv)"
    )
    
    parser.add_argument(
        "--model",
        default="meta-llama/Llama-2-7b-hf",
        help="HuggingFace model name (default: Llama-2-7b-hf)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize bridge
        logger.info("=" * 80)
        logger.info("DSN Attack Bridge - Gradient-Based Token Optimization")
        logger.info("=" * 80)
        
        bridge = DSNGitHubBridge(model_name=args.model)
        
        # Load model
        bridge.load_model_and_tokenizer()
        
        # Process CSV
        bridge.process_csv(args.input, args.output)
        
        logger.info("=" * 80)
        logger.info("✅ DSN Attack completed successfully!")
        logger.info("=" * 80)
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
