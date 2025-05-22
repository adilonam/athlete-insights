import streamlit as st
import pandas as pd

# The function definition is removed, Streamlit will run this file directly when navigated to.

st.title("Athlete Insights Dashboard")
st.markdown("Welcome to the Athlete Insights Dashboard. Analyze and visualize athlete performance data.")
st.markdown("---")

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

if 'athlete_df' in st.session_state:
    current_df = st.session_state.athlete_df
    
    if uploaded_file is None:
        st.info("Displaying previously uploaded data. Upload a new file to replace.")

    if 'Sport' in current_df.columns:
        sports = sorted(current_df['Sport'].unique().tolist())
        sports_options = ["All Sports"] + sports
        
        if 'selected_sport_filter' not in st.session_state or st.session_state.selected_sport_filter not in sports_options:
            st.session_state.selected_sport_filter = "All Sports"

        selected_sport = st.selectbox(
            "Filter by Sport", 
            sports_options, 
            index=sports_options.index(st.session_state.selected_sport_filter),
            key="sport_filter_main_display"
        )
        
        if st.session_state.selected_sport_filter != selected_sport:
            st.session_state.selected_sport_filter = selected_sport

        if selected_sport == "All Sports":
            df_to_display = current_df.copy()
        else:
            df_to_display = current_df[current_df['Sport'] == selected_sport].copy()
        
        st.dataframe(df_to_display, use_container_width=True)

        if 'Test Date' in df_to_display.columns:
            try:
                df_to_display.loc[:, 'Test Date'] = pd.to_datetime(df_to_display['Test Date'])
            except Exception as e:
                st.warning(f"Could not convert 'Test Date' to datetime: {e}. Charts may not display correctly.")

        if not df_to_display.empty and 'Test Code' in df_to_display.columns and 'Value' in df_to_display.columns and 'Test Date' in df_to_display.columns:
            st.markdown("---")
            st.subheader("Progress Charts by Test Code")
            
            df_to_display = df_to_display.sort_values(by='Test Date')

            for test_code in sorted(df_to_display['Test Code'].unique()):
                st.markdown(f"#### Progress for Test Code: {test_code}")
                test_specific_df = df_to_display[df_to_display['Test Code'] == test_code]
                
                if not test_specific_df.empty and 'Athlete Name' in test_specific_df.columns:
                    chart_data = test_specific_df.pivot_table(index='Test Date', columns='Athlete Name', values='Value')
                    st.line_chart(chart_data)
                elif 'Athlete Name' not in test_specific_df.columns:
                    st.warning(f"Cannot plot individual athlete progress for Test Code {test_code} because 'Athlete Name' column is missing.")
        elif 'Test Code' not in df_to_display.columns or 'Value' not in df_to_display.columns or 'Test Date' not in df_to_display.columns:
            st.warning("Required columns ('Test Code', 'Value', 'Test Date') not available in the filtered data to display progress charts.")
    else:
        st.warning("'Sport' column not found in the data. Cannot apply sport filter.")
        st.dataframe(current_df, use_container_width=True)
