import pandas as pd
import re
from typing import Union

# Define tier names as a constant list
TIER_NAMES = ["Tier 1", "Tier 2", "Tier 3", "Tier 4"]

# Helper function to parse condition string like "<=1.50"
def _parse_condition(condition_str: str | None):
    if not condition_str: # Handles None or empty strings from CSV
        return None, None
    
    condition_str = condition_str.strip()
    if not condition_str: # Handles strings that are only whitespace
        return None, None

    # Regex to capture operator (e.g., <=, >=, <, >) and numeric value
    match = re.match(r"([><]=?)\s*(-?\d+\.?\d*)", condition_str)
    if match:
        operator = match.group(1)
        try:
            val = float(match.group(2))
            return operator, val
        except ValueError:
            # If the numeric part isn't a valid float
            return None, None
    return None, None # Pattern does not match (e.g., non-numeric conditions)

# Helper function to check value against parsed condition
def _check_value(current_value: float, operator: str | None, threshold_value: float | None) -> bool:
    if operator is None or threshold_value is None:
        return False
    # Removed print statement
    if operator == "<=":
        return current_value <= threshold_value
    elif operator == "<":
        return current_value < threshold_value
    elif operator == ">=":
        return current_value >= threshold_value
    elif operator == ">":
        return current_value > threshold_value
    return False

def get_tier_for_test(test_code: str, value: Union[float, str]) -> str | None: # Modified signature
    """
    Determines the tier for a given test code and value based on thresholds in a CSV file,
    using pandas for CSV processing.

    Args:
        test_code: The code for the test (e.g., 'A', 'S', 'FL').
        value: The numerical value (for 'Tiered' scoring) or string value 
               (for other scoring types like 'Movement Quality', 'Calculated') 
               achieved by the athlete for the test.

    Returns:
        A string representing the tier (from TIER_NAMES)
        or None if the test code is not found, the scoring type is not applicable,
        the value type is incorrect for the scoring type,
        or the value does not match any defined tier.
    """
    csv_file_path = "./data/notignore/threshold.csv"  # User's path

    try:
        df = pd.read_csv(csv_file_path) # Added comment='//'

        # Find the row matching the test_code
        test_row = df[df['Code'] == test_code]

        if test_row.empty:
            return None # Test code not found

        # Get the first matching row (should be unique by Code)
        row = test_row.iloc[0]
        
        scoring_type = row.get('Scoring Type')
        
        # Use TIER_NAMES constant to get tier condition strings from the row
        tier_conditions_str = [row.get(tier_name) for tier_name in TIER_NAMES]
        
        if scoring_type == 'Tiered':
            if not isinstance(value, (float, int)):
                return None # Value type mismatch for 'Tiered'

            # Parse all conditions first (only relevant for 'Tiered')
            parsed_conditions = [_parse_condition(str(cond_str)) if pd.notna(cond_str) else (None,None) for cond_str in tier_conditions_str]

            # Check Tier 1
            op1, val1 = parsed_conditions[0]
            if _check_value(float(value), op1, val1): # Ensure value is float for _check_value
                return TIER_NAMES[0]
            
            # Check Tier 2
            op2, val2 = parsed_conditions[1]
            if _check_value(float(value), op2, val2):
                return TIER_NAMES[1]
            
            # Check Tier 3
            op3, val3 = parsed_conditions[2]
            if _check_value(float(value), op3, val3):
                return TIER_NAMES[2]
            
            # Check Tier 4
            op4, val4 = parsed_conditions[3]
            if _check_value(float(value), op4, val4):
                return TIER_NAMES[3]
            
            return None # No 'Tiered' condition matched
        
        else: # For other scoring types like 'Movement Quality', 'Calculated'
            if not isinstance(value, str):
                return None # Value type mismatch for string-based scoring

            processed_value = value.strip().lower()
            # TIER_NAMES is now used directly from the module level

            for i, csv_tier_content in enumerate(tier_conditions_str):
                # Ensure content exists and is not just NaN converted to "nan"
                if pd.notna(csv_tier_content) and str(csv_tier_content).strip() != "": 
                    processed_csv_content = str(csv_tier_content).strip().lower()
                    if processed_value == processed_csv_content:
                        return TIER_NAMES[i] # Use the constant list
            
            return None # No string match found in any tier for this scoring type
            
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file_path}")
        return None
    except pd.errors.EmptyDataError: # Specific pandas error for empty CSV
        print(f"Error: CSV file at {csv_file_path} is empty or malformed after filtering comments.")
        return None
    except Exception as e:
        print(f"An error occurred while processing the CSV file with pandas: {e}")
        return None

# Example usage (optional, for testing within this file if run directly):
if __name__ == '__main__':
    # Make sure threshold.csv is in the specified path for these examples to work
    
    # Example 1: 10-Yard Sprint (Code A, Tiered, lower is better)
    # Tier 1: <=1.50, Tier 2: <=1.55, Tier 3: <=1.60, Tier 4: >1.60
    print(f"Test A, Value 1.48: {get_tier_for_test('A', 1.48)}")  # Expected: Tier 1


    # Example 4: Dynamic Strength Index (Code DSI, Calculated, string match)
    # Tier 1: Pain, Tier 2: Balanced, Tier 3: Outside Ideal, Tier 4: No Limitation
    print(f"Test DSI, Value 'Balanced': {get_tier_for_test('DSI', 'Balanced')}") # Expected: Tier 2
    print(f"Test DSI, Value 'pain': {get_tier_for_test('DSI', 'Pain')}")       # Expected: Tier 1 (case-insensitive)
