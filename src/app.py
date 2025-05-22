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
            temp_uploaded_df = pd.read_csv(uploaded_file)
            all_checks_passed = True

            # 1. Required Column Check
            required_cols = ["Athlete Name", "Test Date", "Sport", "Test Name", "Test Code", "Value"]
            missing_required_cols = [col for col in required_cols if col not in temp_uploaded_df.columns]

            if missing_required_cols:
                st.error(f"Uploaded file is missing the following required columns: {', '.join(missing_required_cols)}. Please correct the file and re-upload.")
                all_checks_passed = False
            
            # 2. Test Code Existence Check (only if required columns are present)
            if all_checks_passed:
                if not test_name_code_df.empty and 'Test Code' in temp_uploaded_df.columns:
                    missing_codes_df = temp_uploaded_df[~temp_uploaded_df['Test Code'].isin(test_name_code_df['Test Code'])]
                    if not missing_codes_df.empty:
                        missing_info = [f"Index {index}: {row['Test Code']}" for index, row in missing_codes_df.iterrows()]
                        st.error(f"The following Test Codes in the uploaded file are not found in the available tests: {'; '.join(missing_info)}")
                        all_checks_passed = False
                elif 'Test Code' not in temp_uploaded_df.columns: # Should be caught by required_cols if 'Test Code' is in it.
                    st.error("Uploaded file is missing the 'Test Code' column.")
                    all_checks_passed = False
            
            st.dataframe(temp_uploaded_df, use_container_width=True)
            
            if all_checks_passed:
                st.success("File uploaded and validated successfully!")
                st.session_state.athlete_df = temp_uploaded_df
                # Reset sport filter for new data and trigger a rerun to update display
                st.session_state.selected_sport_filter = "All Sports" 
            # If checks fail, athlete_df in session is not updated, no automatic rerun here.

        except Exception as e:
            st.error(f"Error processing uploaded file: {e}")
            if 'athlete_df' in st.session_state: # Optionally clear session state on critical error
                del st.session_state.athlete_df


    # Unified Data Display and Filtering Block
    if 'athlete_df' in st.session_state:
        current_df = st.session_state.athlete_df
        
        # Show info message only if displaying data from session, not a fresh upload
        if uploaded_file is None:
            st.info("Displaying previously uploaded data. Upload a new file to replace.")

        if 'Sport' in current_df.columns:
            sports = sorted(current_df['Sport'].unique().tolist())
            sports_options = ["All Sports"] + sports
            
            # Initialize or retrieve selected_sport from session state
            if 'selected_sport_filter' not in st.session_state or st.session_state.selected_sport_filter not in sports_options:
                st.session_state.selected_sport_filter = "All Sports"

            selected_sport = st.selectbox(
                "Filter by Sport", 
                sports_options, 
                index=sports_options.index(st.session_state.selected_sport_filter),
                key="sport_filter_main_display"
            )
            
            # If user changes the filter, update session state and rerun
            if st.session_state.selected_sport_filter != selected_sport:
                st.session_state.selected_sport_filter = selected_sport

            if selected_sport == "All Sports":
                df_to_display = current_df
            else:
                df_to_display = current_df[current_df['Sport'] == selected_sport]
            
            st.dataframe(df_to_display, use_container_width=True)

            # Convert 'Test Date' to datetime objects for plotting
            if 'Test Date' in df_to_display.columns:
                try:
                    df_to_display['Test Date'] = pd.to_datetime(df_to_display['Test Date'])
                except Exception as e:
                    st.warning(f"Could not convert 'Test Date' to datetime: {e}. Charts may not display correctly.")

            if not df_to_display.empty and 'Test Code' in df_to_display.columns and 'Value' in df_to_display.columns and 'Test Date' in df_to_display.columns:
                st.markdown("---")
                st.subheader("Progress Charts by Test Code")
                
                # Ensure 'Test Date' is sorted for line charts
                df_to_display = df_to_display.sort_values(by='Test Date')

                for test_code in sorted(df_to_display['Test Code'].unique()):
                    st.markdown(f"#### Progress for Test Code: {test_code}")
                    test_specific_df = df_to_display[df_to_display['Test Code'] == test_code]
                    
                    if not test_specific_df.empty:
                        # Prepare data for charting: index by Test Date, select Value
                        chart_data = test_specific_df.set_index('Test Date')[['Value']]
                        st.line_chart(chart_data)
                    else:
                        st.write("No data available for this test code in the current selection.")
            elif 'Test Code' not in df_to_display.columns or 'Value' not in df_to_display.columns or 'Test Date' not in df_to_display.columns:
                st.warning("Required columns ('Test Code', 'Value', 'Test Date') not available in the filtered data to display progress charts.")

        else:
            # This case implies 'Sport' column is missing, even if other checks passed (e.g. if 'Sport' wasn't in required_cols)
            # Or if 'athlete_df' was set in session by some other means without 'Sport'
            st.warning("'Sport' column not found in the data. Cannot apply sport filter.")
            st.dataframe(current_df, use_container_width=True) # Display unfiltered data


elif page == "Thresholds Management":
    st.title("Performance Thresholds Management")
    st.markdown("Edit the thresholds directly in the table below. Changes will be automatically saved.")
