import streamlit as st
import pandas as pd
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

# Initialize athlete_df in session state if it doesn't exist
if 'athlete_df' not in st.session_state:
    st.session_state.athlete_df = pd.DataFrame()

test_name_code_df = pd.DataFrame()
try:
    threshold_df = pd.read_csv("data/notignore/threshold.csv")
    
    test_name_code_df = threshold_df.drop_duplicates(subset=["Code"])[["Code", "Test Name"]]
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
tab1, tab2 = st.tabs(["Upload CSV", "Manual Entry"])

# Tab 1: Upload CSV file
with tab1:
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

# Tab 2: Manual Entry
with tab2:
    with st.form("manual_entry_form"):
        st.subheader("Enter Athlete Data Manually")
        
        # Form inputs matching the CSV structure
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
        
        value = st.number_input("Value", format="%.2f")
        
        submit_button = st.form_submit_button("Add Entry")
        
        if submit_button and athlete_name and sport and test_name and test_code:
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

# Display the DataFrame AFTER processing the upload
# Add tier information to the athlete dataframe
st.session_state.athlete_df = add_tier_to_df(st.session_state.athlete_df)

if st.button("Clear Athlete Data"):
    st.session_state.athlete_df = pd.DataFrame()

st.dataframe(st.session_state.athlete_df, use_container_width=True)

