import streamlit as st
import pandas as pd
# Set page configuration
st.set_page_config(
    page_title="Athlete Insights",
    page_icon="🏃",
    layout="wide"
)

st.title("Athlete Insights")
st.markdown("Welcome to Athlete Insights! Use the sidebar to navigate to different sections.")

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
except Exception as e:
    st.error(f"Error loading threshold data: {e}")
    
st.markdown("---")
st.subheader("Upload Athlete Data")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        temp_uploaded_df = pd.read_csv(uploaded_file)
        all_checks_passed = True

        required_cols = ["Athlete Name", "Test Date", "Sport", "Test Name", "Test Code", "Value"]
        missing_required_cols = [col for col in required_cols if col not in temp_uploaded_df.columns]

        if missing_required_cols:
            st.error(f"Uploaded file is missing the following required columns: {', '.join(missing_required_cols)}. Please correct the file and re-upload.")
            all_checks_passed = False
        
        if all_checks_passed:
            if not test_name_code_df.empty and 'Test Code' in temp_uploaded_df.columns:
                missing_codes_df = temp_uploaded_df[~temp_uploaded_df['Test Code'].isin(test_name_code_df['Test Code'])]
                if not missing_codes_df.empty:
                    missing_info = [f"Index {index}: {row['Test Code']}" for index, row in missing_codes_df.iterrows()]
                    st.error(f"The following Test Codes in the uploaded file are not found in the available tests: {'; '.join(missing_info)}")
                    all_checks_passed = False
            elif 'Test Code' not in temp_uploaded_df.columns:
                st.error("Uploaded file is missing the 'Test Code' column.")
                all_checks_passed = False
        
        st.dataframe(temp_uploaded_df, use_container_width=True)
        
        if all_checks_passed:
            st.success("File uploaded and validated successfully!")
            st.session_state.athlete_df = temp_uploaded_df
            st.session_state.selected_sport_filter = "All Sports" 
        
    except Exception as e:
        st.error(f"Error processing uploaded file: {e}")
        if 'athlete_df' in st.session_state:
            del st.session_state.athlete_df
# Streamlit will automatically find and run pages from the 'pages' directory.
# No explicit routing is needed here anymore.

# The content of what was previously the default page (main_dashboard) 
# can either be moved here to app.py to serve as the landing page,
# or main_dashboard.py can be renamed to something like 01_Main_Dashboard.py 
# in the pages folder to control its order and make it the default.
# For now, app.py will just show a welcome message.
