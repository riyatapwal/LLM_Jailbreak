"""
Bijection Output Verification Script

This script verifies that the bijection encoding in the output CSV is correct
by decoding each encoded prompt using its mapping and comparing with the original.

Usage:
    python verify_bijection_output.py <output_csv_file>

Example:
    python verify_bijection_output.py output_test.csv
"""

import csv
import json
import sys
from pathlib import Path


def verify_bijection_output(csv_file):
    """
    Verify bijection encoding by decoding and comparing with originals.
    
    Args:
        csv_file (str): Path to the output CSV file with bijection_mapping column
        
    Returns:
        tuple: (verified_count, failed_count)
    """
    
    # Check if file exists
    if not Path(csv_file).exists():
        print(f"Error: File not found: {csv_file}")
        return 0, 0
    
    verified = 0
    failed = 0
    failed_details = []
    
    print(f"Verifying bijection output from: {csv_file}")
    print("=" * 80)
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Validate required columns exist
        if reader.fieldnames is None:
            print("Error: CSV file is empty or invalid")
            return 0, 0
            
        required_cols = ['seed_prompt_text', 'attack_prompt_text', 'bijection_mapping']
        missing_cols = [col for col in required_cols if col not in reader.fieldnames]
        if missing_cols:
            print(f"Error: Missing required columns: {missing_cols}")
            return 0, 0
        
        row_num = 0
        for row in reader:
            row_num += 1
            
            try:
                original = row['seed_prompt_text']
                encoded = row['attack_prompt_text']
                mapping_json = row['bijection_mapping']
                attack_id = row.get('Attack_prompt_id', f'row_{row_num}')
                
                # Parse the mapping dictionary from JSON
                mapping = json.loads(mapping_json)
                
                # Create inverse mapping (for decoding)
                inverse_mapping = {v: k for k, v in mapping.items()}
                
                # Decode the encoded prompt
                decoded = "".join(inverse_mapping.get(c, c) for c in encoded)
                
                # Compare original with decoded (convert original to lowercase for comparison)
                # because bijection encoder works on lowercase characters
                original_lower = original.lower()
                if decoded == original_lower:
                    verified += 1
                    print(f"✓ Row {row_num} ({attack_id}): VERIFIED")
                    print(f"  Original: {original_lower[:70]}...")
                    print(f"  Decoded:  {decoded[:70]}...")
                    print()
                else:
                    failed += 1
                    print(f"✗ Row {row_num} ({attack_id}): FAILED")
                    failed_details.append({
                        'row': row_num,
                        'attack_id': attack_id,
                        'original': original[:60],
                        'decoded': decoded[:60]
                    })
                    
            except json.JSONDecodeError as e:
                failed += 1
                print(f"✗ Row {row_num}: JSON PARSE ERROR - {str(e)}")
                failed_details.append({
                    'row': row_num,
                    'error': f'JSON Parse Error: {str(e)}'
                })
            except Exception as e:
                failed += 1
                print(f"✗ Row {row_num}: ERROR - {str(e)}")
                failed_details.append({
                    'row': row_num,
                    'error': str(e)
                })
    
    # Print summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"✓ Verified:  {verified}")
    print(f"✗ Failed:    {failed}")
    print(f"Total:       {verified + failed}")
    
    if verified + failed > 0:
        success_rate = (verified / (verified + failed)) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    # Show failed details if any
    if failed_details:
        print("\n" + "=" * 80)
        print("FAILED ROWS DETAILS")
        print("=" * 80)
        for detail in failed_details:
            print(f"\nRow {detail.get('row')}:")
            if 'error' in detail:
                print(f"  Error: {detail['error']}")
            else:
                print(f"  Attack ID: {detail.get('attack_id')}")
                print(f"  Original (first 60 chars): {detail.get('original')}")
                print(f"  Decoded  (first 60 chars): {detail.get('decoded')}")
    
    print("\n" + "=" * 80)
    
    return verified, failed


if __name__ == "__main__":
    """
    Command-line interface for verifying bijection output CSV.
    
    Usage:
        python verify_bijection_output.py <output_csv_path>
    
    Args:
        output_csv_path (str): Path to the output CSV file to verify
    
    Examples:
        python verify_bijection_output.py output_test.csv
        python verify_bijection_output.py /path/to/output.csv
    """
    
    # Check for required argument
    if len(sys.argv) < 2:
        print("Usage: python verify_bijection_output.py <output_csv_path>")
        print("\nExample:")
        print("  python verify_bijection_output.py output_test.csv")
        sys.exit(1)
    
    # Get CSV file path from argument
    csv_file = sys.argv[1]
    
    # Run verification
    verified, failed = verify_bijection_output(csv_file)
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)
