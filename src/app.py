import streamlit as st
import pandas as pd


# Set page configuration
st.set_page_config(
    page_title="Athlete Insights",
    page_icon="🏃",
    layout="wide"
)

# Sidebar Navigation
with st.sidebar:
    st.title("📊 Navigation")
    st.markdown("---")
    
    # Use session state to track current page if not already set
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Main Dashboard"
    
    # Navigation buttons with icons and styling
    if st.button("🏃 Main Dashboard", use_container_width=True, type="primary" if st.session_state.current_page == "Main Dashboard" else "secondary"):
        st.session_state.current_page = "Main Dashboard"
        st.rerun()
    
    if st.button("⚙️ Thresholds Management", use_container_width=True, type="primary" if st.session_state.current_page == "Thresholds Management" else "secondary"):
        st.session_state.current_page = "Thresholds Management"
        st.rerun()
    
    st.markdown("---")
    page = st.session_state.current_page




if page == "Main Dashboard":
    st.title("Athlete Insights Dashboard")
    st.markdown("Welcome to the Athlete Insights Dashboard. Analyze and visualize athlete performance data.")
    st.markdown("---") # Add a separator

    test_name_code_df = pd.DataFrame() # Initialize test_name_code_df
    try:
        threshold_df = pd.read_csv("data/notignore/threshold.csv")
        
        # Drop duplicates based only on the "Code" column, keeping the first Test Name associated
        test_name_code_df = threshold_df.drop_duplicates(subset=["Code"])[["Code", "Test Name"]]
        # Rename "Code" column to "Test Code"
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
            uploaded_df = pd.read_csv(uploaded_file)
            st.session_state.athlete_df = uploaded_df # Save to session state
            st.success("File uploaded successfully!")

            # Check for Test Code existence
            if not test_name_code_df.empty and 'Test Code' in uploaded_df.columns:
                missing_codes_df = uploaded_df[~uploaded_df['Test Code'].isin(test_name_code_df['Test Code'])]
                if not missing_codes_df.empty:
                    missing_info = []
                    for index, row in missing_codes_df.iterrows():
                        missing_info.append(f"Index {index}: {row['Test Code']}")
                    st.warning(f"The following Test Codes in the uploaded file are not found in the available tests: {'; '.join(missing_info)}")
                else:
                    st.success("All Test Codes in the uploaded file are valid.")
            elif 'Test Code' not in uploaded_df.columns:
                st.error("Uploaded file is missing the 'Test Code' column.")
            
            st.dataframe(uploaded_df, use_container_width=True)
        except Exception as e:
            st.error(f"Error processing uploaded file: {e}")
    elif 'athlete_df' in st.session_state: # Check if data already exists in session state
        st.info("Displaying previously uploaded data. Upload a new file to replace.")
        st.dataframe(st.session_state.athlete_df, use_container_width=True)


    


elif page == "Thresholds Management":
    st.title("Performance Thresholds Management")
    st.markdown("Edit the thresholds directly in the table below. Changes will be automatically saved.")
