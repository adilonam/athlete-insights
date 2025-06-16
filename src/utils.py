import pandas as pd
import re
from typing import Union, Tuple, List


# Define tier names as a constant list
TIER_NAMES = ["Tier 1", "Tier 2", "Tier 3", "Tier 4"]
TIER_MAP = {name: 3 - i for i, name in enumerate(TIER_NAMES)}

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

def check_athlete_df(df: pd.DataFrame, test_name_code_df: pd.DataFrame, 
                    sports_list: list) -> Tuple[bool, List[str]]:
    """
    Validates athlete data against required columns, test codes, and sports.
    
    Args:
        df: DataFrame containing athlete data
        test_name_code_df: DataFrame containing valid test codes and names
        sports_list: List of valid sports
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    all_checks_passed = True
    error_messages = []
    
    # Check required columns
    required_cols = ["Athlete Name", "Test Date", "Sport", "Test Name", "Test Code", "Value"]
    missing_required_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_required_cols:
        error_messages.append(f"Missing required columns: {', '.join(missing_required_cols)}")
        all_checks_passed = False
    
    if all_checks_passed:
        # Check test codes
        if not test_name_code_df.empty and 'Test Code' in df.columns:
            missing_codes_df = df[~df['Test Code'].isin(test_name_code_df['Test Code'])]
            if not missing_codes_df.empty:
                missing_info = [f"Index {index}: {row['Test Code']}" for index, row in missing_codes_df.iterrows()]
                error_messages.append(f"The following Test Codes are not found in the available tests: {'; '.join(missing_info)}")
                all_checks_passed = False
        
        # Check sports
        if 'Sport' in df.columns:
            invalid_sports = df[~df['Sport'].isin(sports_list)]
            if not invalid_sports.empty:
                invalid_sport_info = [f"Index {index}: {row['Sport']}" for index, row in invalid_sports.iterrows()]
                error_messages.append(f"The following Sports are not valid: {'; '.join(invalid_sport_info)}. Valid sports are: {', '.join(sports_list)}")
                all_checks_passed = False
    
    return all_checks_passed, error_messages

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
            if not str(value).replace('.', '').replace('-', '').isdigit():
                return None # Value type mismatch for 'Tiered'

            # Parse all conditions first (only relevant for 'Tiered')
            parsed_conditions = [_parse_condition(str(cond_str)) if pd.notna(cond_str) else (None,None) for cond_str in tier_conditions_str]

            # Convert value to float for comparison
            float_value = float(value)
            # Check all tiers in a loop
            for i, (operator, threshold) in enumerate(parsed_conditions):
                if _check_value(float_value, operator, threshold):
                    return TIER_MAP[TIER_NAMES[i]]

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
                        return TIER_MAP[TIER_NAMES[i]] # Use the constant list

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


# Function to add tier information to athlete dataframe
def add_tier_to_df(df):
    if df.empty:
        return df
    if "Tier Number" in df.columns:
        df.drop(columns=["Tier Number"], inplace=True)
    # Create a new 'Tier Number' column and apply get_tier_for_test using pandas apply
    df.insert(df.columns.get_loc('Test Code') + 1, 'Tier Number', 
              df.apply(lambda row: get_tier_for_test(row['Test Code'], row['Value']), axis=1))
    
    return df

# Example usage (optional, for testing within this file if run directly):
if __name__ == '__main__':
    # Make sure threshold.csv is in the specified path for these examples to work
    
    # Example 1: 10-Yard Sprint (Code A, Tiered, lower is better)
    # Tier 1: <=1.50, Tier 2: <=1.55, Tier 3: <=1.60, Tier 4: >1.60
    print(f"Test A, Value 19.74: {get_tier_for_test('A', 1.48)}")  # Expected: Tier 1


    # Example 4: Dynamic Strength Index (Code DSI, Calculated, string match)
    # Tier 1: Pain, Tier 2: Balanced, Tier 3: Outside Ideal, Tier 4: No Limitation
    print(f"Test DSI, Value 'Balanced': {get_tier_for_test('DSI', 'Balanced')}") # Expected: Tier 2
    print(f"Test DSI, Value 'pain': {get_tier_for_test('DSI', 'Pain')}")       # Expected: Tier 1 (case-insensitive)
