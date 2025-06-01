import streamlit as st
import pandas as pd
import os
from utils import check_athlete_df, add_tier_to_df

# Set page configuration
st.set_page_config(
    page_title="Athlete Insights",
    page_icon="🏃",
    layout="wide"
)

# Load sports from CSV file
try:
    sports_df = pd.read_csv("./data/notignore/sports.csv")
    SPORTS = sports_df["Name"].tolist()
except Exception as e:
    # Fallback to default sports if file cannot be loaded
    SPORTS = []
    st.error(f"Error loading sports data: {e}. Using default sports list.")

st.title("Athlete Insights")
st.markdown("Welcome to Athlete Insights! Use the sidebar to navigate to different sections.")
ATHLETE_CSV_PATH = "./data/notignore/athlete_data.csv"
# Initialize athlete_df in session state if it doesn't exist
if 'athlete_df' not in st.session_state:
    # Try to load athlete data from CSV if it exists
    try:
        athlete_data_path = ATHLETE_CSV_PATH
        if os.path.exists(athlete_data_path):
            st.session_state.athlete_df = pd.read_csv(athlete_data_path)
            # Add tier information to the dataframe
            st.session_state.athlete_df = add_tier_to_df(st.session_state.athlete_df)
        else:
            st.session_state.athlete_df = pd.DataFrame()
    except Exception as e:
        st.session_state.athlete_df = pd.DataFrame()
        st.warning(f"Could not load existing athlete data: {e}")

test_name_code_df = pd.DataFrame()
try:
    threshold_df = pd.read_csv("data/notignore/threshold.csv")
    
    test_name_code_df = threshold_df.drop_duplicates(subset=["Code"])
    test_name_code_df = test_name_code_df.rename(columns={"Code": "Test Code"})
    
    st.subheader("Available Tests (Code and Name)")
    if not test_name_code_df.empty:
        st.dataframe(test_name_code_df, use_container_width=True)
    else:
        st.write("No test codes found.")
        
    # Display available sports
    st.subheader("Available Sports")
    st.write(", ".join(SPORTS))
except Exception as e:
    st.error(f"Error loading threshold data: {e}")
    
st.markdown("---")
st.subheader("Add Athlete Data")

# Create tabs for different input methods
tab1, tab2 = st.tabs(["Manual Entry", "Upload CSV"])

# Tab 1: Manual Entry
with tab1:
    st.subheader("Enter Athlete Data Manually")
    
    # Form inputs matching the CSV structure (outside form for dynamic updates)
    athlete_name = st.text_input("Athlete Name")
    test_date = st.date_input("Test Date")
    sport = st.selectbox("Sport", SPORTS)
    
    # If test codes are available, use them in a dropdown
    if not test_name_code_df.empty:
        test_options = {row['Test Name']: row['Test Code'] for _, row in test_name_code_df.iterrows()}
        test_name = st.selectbox("Test Name", list(test_options.keys()))
        test_code = test_options[test_name]
    else:
        test_name = st.text_input("Test Name")
        test_code = st.text_input("Test Code")
    
    # Initialize value variable
    value = None
    
    if test_code and test_name:
        st.write(f"Selected Test Code: {test_code} for Test Name: {test_name}")
        _df = test_name_code_df[test_name_code_df['Test Code'] == test_code]
        
        if not _df.empty:
            scoring_type = _df['Scoring Type'].values[0]
            
            if scoring_type == 'Tiered':
                value = st.number_input("Value (for Tiered tests)", min_value=0.0, step=0.1)
            else:
                # For Movement Quality and Calculated scoring types, use the tier options
                tier_options = _df[["Tier 1", "Tier 2", "Tier 3", "Tier 4"]].values.flatten()
                # Remove NaN values and convert to list
                tier_options = [str(opt) for opt in tier_options if pd.notna(opt)]
                
                if tier_options:
                    value = st.selectbox(
                        f"Value (for {scoring_type} tests)",
                        options=tier_options,
                        help="Select the appropriate value for the test"
                    )
                else:
                    value = st.text_input("Value", help="Enter the value for this test")
    
    # Form for submission only
    with st.form("manual_entry_form"):
        submit_button = st.form_submit_button("Add Entry")
        
        if submit_button and athlete_name and sport and test_name and test_code and value is not None:
            # Create new entry
            new_entry = pd.DataFrame({
                "Athlete Name": [athlete_name],
                "Test Date": [test_date.strftime("%-m/%-d/%Y")],  # Format to match the CSV format
                "Sport": [sport],
                "Test Name": [test_name],
                "Test Code": [test_code],
                "Value": [value]
            })
            
            # Validate the entry
            all_checks_passed, error_messages = check_athlete_df(
                new_entry,
                test_name_code_df,
                SPORTS
            )
            
            if all_checks_passed:
                # Add tier information to the new entry
                new_entry_with_tier = add_tier_to_df(new_entry)
                
                # Add to existing dataframe
                if 'athlete_df' in st.session_state and not st.session_state.athlete_df.empty:
                    st.session_state.athlete_df = pd.concat([st.session_state.athlete_df, new_entry_with_tier], ignore_index=True)
                else:
                    st.session_state.athlete_df = new_entry_with_tier
                    
                st.success(f"Entry added for {athlete_name}")
                st.session_state.selected_sport_filter = "All Sports"
            else:
                # Display validation errors
                for error_msg in error_messages:
                    st.error(error_msg)

# Tab 2: Upload CSV file
with tab2:
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            temp_uploaded_df = pd.read_csv(uploaded_file)
            
            # Use the check_athlete_df function from utils
            all_checks_passed, error_messages = check_athlete_df(
                temp_uploaded_df, 
                test_name_code_df,
                SPORTS
            )
            
            # Display any error messages
            for error_msg in error_messages:
                st.error(error_msg)
            
            if all_checks_passed:
                st.success("File uploaded and validated successfully!")
                # Add tier information to the dataframe
                st.session_state.athlete_df = add_tier_to_df(temp_uploaded_df)
                st.session_state.selected_sport_filter = "All Sports" 
            
        except Exception as e:
            st.error(f"Error processing uploaded file: {e}")
            if 'athlete_df' in st.session_state:
                del st.session_state.athlete_df

# Display the DataFrame AFTER processing the upload
# Add tier information to the athlete dataframe

st.markdown("---")
st.subheader("Athlete Data Management")

# Create a key that will change when we want to refresh the data editor
if 'editor_key' not in st.session_state:
    st.session_state.editor_key = 0

# Create a data editor for the athlete data
edited_athlete_df = st.data_editor(
    st.session_state.athlete_df, 
    use_container_width=True,
    num_rows="dynamic",
    key=f"athlete_data_editor_{st.session_state.editor_key}",
    column_config={
        "Athlete Name": st.column_config.TextColumn("Athlete Name", help="Name of the athlete"),
        "Test Date": st.column_config.TextColumn("Test Date", help="Date of the test (M/D/YYYY)"),
        "Sport": st.column_config.SelectboxColumn(
            "Sport",
            help="Sport of the athlete",
            options=SPORTS,
            required=True
        ),
        "Test Name": st.column_config.TextColumn("Test Name", help="Name of the test"),
        "Test Code": st.column_config.TextColumn("Test Code", help="Code of the test"),
        "Value": st.column_config.TextColumn("Value", help="Value of the test"),
        "Tier Number": st.column_config.NumberColumn("Tier Number", help="Performance tier (1-4)", min_value=1, max_value=4)
    },
    disabled=["Tier Number"]  # Make Tier Number read-only as it's calculated
)

# Keep track of the current data editor values
st.session_state.athlete_df = edited_athlete_df

# Action buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Refresh Tier Number", help="Recalculate the Tier Number for all athletes"):
        # Update the data with fresh tier calculations
        st.session_state.athlete_df = add_tier_to_df(st.session_state.athlete_df)
        # Increment the key to force the data editor to refresh
        st.session_state.editor_key += 1
        # This will cause a rerun with the new key and updated data
        st.rerun()

with col2:
    if st.button("Clear Athlete Data", help="Remove all athlete data from the table"):
        st.session_state.athlete_df = pd.DataFrame()
        # Increment the key to force the data editor to refresh
        st.session_state.editor_key += 1
        st.success("All data cleared!")
        st.rerun()

with col3:
    if st.button("Save to local", help="Save the current athlete data to a CSV file"):
        try:
            # Apply tier calculations before saving
            df_to_save = add_tier_to_df(st.session_state.athlete_df)
            # Save to CSV file
            df_to_save.to_csv(ATHLETE_CSV_PATH, index=False)
            st.success("Data saved to athlete_data.csv successfully!")
        except Exception as e:
            st.error(f"Error saving data: {e}")
