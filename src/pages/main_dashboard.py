import streamlit as st
import pandas as pd
import plotly.express as px

# The function definition is removed, Streamlit will run this file directly when navigated to.

st.title("Athlete Insights Dashboard")
st.markdown("Welcome to the Athlete Insights Dashboard. Analyze and visualize athlete performance data.")
st.markdown("---")


if 'athlete_df' in st.session_state:
    current_df = st.session_state.athlete_df
    
  
    # Create filter columns
    col1, col2, col3 = st.columns([2, 2, 1])
    
    # Initialize session state for filters if not exists
    if 'applied_sport_filter' not in st.session_state:
        st.session_state.applied_sport_filter = "All Sports"
    if 'applied_athlete_filter' not in st.session_state:
        st.session_state.applied_athlete_filter = "All Athletes"
    
    if 'Sport' in current_df.columns:
        with col1:
            sports = sorted(current_df['Sport'].unique().tolist())
            sports_options = ["All Sports"] + sports
            
            selected_sport = st.selectbox(
                "Filter by Sport", 
                sports_options,
                key="sport_selectbox"
            )
    else:
        selected_sport = "All Sports"
    
    if 'Athlete Name' in current_df.columns:
        with col2:
            athletes = sorted(current_df['Athlete Name'].unique().tolist())
            athletes_options = ["All Athletes"] + athletes
            
            selected_athlete = st.selectbox(
                "Filter by Athlete", 
                athletes_options,
                key="athlete_selectbox"
            )
    else:
        selected_athlete = "All Athletes"
    
    # Apply Filters button
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing to align with selectboxes
        if st.button("Apply Filters", type="primary"):
            st.session_state.applied_sport_filter = selected_sport
            st.session_state.applied_athlete_filter = selected_athlete
            st.rerun()
    
    # Show Best Records button
    if st.button("Show Best Records", type="secondary"):
        if st.session_state.applied_athlete_filter != "All Athletes" and st.session_state.applied_sport_filter != "All Sports":
            # Filter data for the selected athlete and sport
            best_records_df = current_df[
                (current_df['Athlete Name'] == st.session_state.applied_athlete_filter) & 
                (current_df['Sport'] == st.session_state.applied_sport_filter)
            ]
            
            if not best_records_df.empty and 'Test Code' in best_records_df.columns and 'Tier Number' in best_records_df.columns:
                # Find the best (highest) tier number for each test code
                best_records = best_records_df.groupby('Test Code')['Tier Number'].max().reset_index()
                
                # Create the formatted string like "A3-B2"
                record_parts = []
                for _, row in best_records.iterrows():
                    record_parts.append(f"{row['Test Code']}{row['Tier Number']}")
                
                best_record_string = "-".join(record_parts)
                
                st.success(f"**Best Records for {st.session_state.applied_athlete_filter} in {st.session_state.applied_sport_filter}:** {best_record_string}")
            else:
                st.warning("No records found for the selected athlete and sport.")
        else:
            st.warning("Please select both a specific athlete and sport to view best records.")
    
    # Reset Filters button
    if st.button("Reset Filters"):
        st.session_state.applied_sport_filter = "All Sports"
        st.session_state.applied_athlete_filter = "All Athletes"
        st.rerun()

    # Apply filters based on session state (applied filters, not selected filters)
    df_to_display = current_df.copy()
    
    if 'Sport' in current_df.columns and st.session_state.applied_sport_filter != "All Sports":
        df_to_display = df_to_display[df_to_display['Sport'] == st.session_state.applied_sport_filter]
    
    if 'Athlete Name' in current_df.columns and st.session_state.applied_athlete_filter != "All Athletes":
        df_to_display = df_to_display[df_to_display['Athlete Name'] == st.session_state.applied_athlete_filter]
    
    # Show current active filters
    if st.session_state.applied_sport_filter != "All Sports" or st.session_state.applied_athlete_filter != "All Athletes":
        st.info(f"**Active Filters:** Sport: {st.session_state.applied_sport_filter} | Athlete: {st.session_state.applied_athlete_filter}")
    
    # Display the filtered data
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
                # Check if values are numeric or categorical
                sample_values = test_specific_df['Value'].dropna()
                if not sample_values.empty:
                    # Try to convert to numeric to determine if it's numeric data
                    numeric_values = pd.to_numeric(sample_values, errors='coerce')
                    is_numeric = not numeric_values.isna().all()
                    
                    if is_numeric:
                        # For numeric data, convert to float and use line chart
                        test_specific_df_numeric = test_specific_df.copy()
                        test_specific_df_numeric['Value'] = pd.to_numeric(test_specific_df_numeric['Value'], errors='coerce')
                        chart_data = test_specific_df_numeric.pivot_table(index='Test Date', columns='Athlete Name', values='Value')
                        st.line_chart(chart_data)
                    else:
                        # For categorical/string data, use scatter plot with string values on y-axis
                        # Prepare data for plotly
                        plot_data = test_specific_df.copy()
                        plot_data['Test Date'] = pd.to_datetime(plot_data['Test Date'])
                        
                        # Create scatter plot with lines
                        fig = px.line(plot_data, 
                                    x='Test Date', 
                                    y='Value', 
                                    color='Athlete Name',
                                    title=f'Progress for {test_code}',
                                    markers=True)
                        
                        # Update layout for better readability
                        fig.update_layout(
                            xaxis_title="Test Date",
                            yaxis_title="Value",
                            height=400
                        )
                        
                        # Display the plotly chart
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No data available for Test Code {test_code}")
            elif 'Athlete Name' not in test_specific_df.columns:
                st.warning(f"Cannot plot individual athlete progress for Test Code {test_code} because 'Athlete Name' column is missing.")
    elif 'Test Code' not in df_to_display.columns or 'Value' not in df_to_display.columns or 'Test Date' not in df_to_display.columns:
        st.warning("Required columns ('Test Code', 'Value', 'Test Date') not available in the filtered data to display progress charts.")
else:
    st.warning("No athlete data loaded. Please upload data first.")
