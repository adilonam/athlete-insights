import streamlit as st
import pandas as pd
from utils import (
    PERFORMANCE_METRICS, MOVEMENT_METRICS, MOVEMENT_OPTIONS,
    create_new_entry, combine_data, create_performance_chart,
    create_movement_assessment_chart
)
from thresholds import get_threshold_df, apply_thresholds, DEFAULT_THRESHOLDS

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

# Initialize session state for storing manual entries and thresholds
if 'manual_entries' not in st.session_state:
    st.session_state.manual_entries = pd.DataFrame()
if 'thresholds_df' not in st.session_state:
    st.session_state.thresholds_df = get_threshold_df()

if page == "Main Dashboard":
    st.title("Athlete Insights Dashboard")
    st.markdown("Welcome to the Athlete Insights Dashboard. Analyze and visualize athlete performance data.")

    # Create tabs for file upload and manual entry
    tab1, tab2 = st.tabs(["Upload CSV", "Manual Entry"])

    with tab1:
        uploaded_file = st.file_uploader("Upload Athlete Data CSV", type=['csv'])

    with tab2:
        st.subheader("Manual Data Entry")
        with st.form("data_entry_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                form_data = {
                    'athlete_name': st.text_input("Athlete Name"),
                    'test_date': st.date_input("Test Date"),
                    'sport': st.text_input("Sport"),
                    'sprint_10': st.number_input("0-10 Yard Sprint (s)", min_value=0.0, format="%.2f"),
                    'fly_10': st.number_input("Fly-10 (s)", min_value=0.0, format="%.2f"),
                    'pro_agility': st.number_input("Pro-Agility (s)", min_value=0.0, format="%.2f")
                }
            
            with col2:
                form_data.update({
                    'mtp_force': st.number_input("MTP Peak Force (N)", min_value=0.0, format="%.1f"),
                    'chin_up': st.number_input("Chin-Up Strength (Reps)", min_value=0),
                    'cmj': st.number_input("CMJ (in)", min_value=0.0, format="%.1f"),
                    'ncmj': st.number_input("NCMJ (in)", min_value=0.0, format="%.1f"),
                    'med_ball': st.number_input("Seated Med Ball Throw (ft)", min_value=0.0, format="%.1f"),
                    'rsi': st.number_input("5-Jump RSI", min_value=0.0, format="%.2f")
                })
                
            with col3:
                form_data.update({
                    'm_ohs': st.selectbox("M-OHS", MOVEMENT_OPTIONS),
                    'm_hs': st.selectbox("M-HS", MOVEMENT_OPTIONS),
                    'm_il': st.selectbox("M-IL", MOVEMENT_OPTIONS),
                    'm_sm': st.selectbox("M-SM", MOVEMENT_OPTIONS),
                    'm_aslr': st.selectbox("M-ASLR", MOVEMENT_OPTIONS),
                    'm_tspu': st.selectbox("M-TSPU", MOVEMENT_OPTIONS),
                    'm_rs': st.selectbox("M-RS", MOVEMENT_OPTIONS),
                    'm_ubmc': st.selectbox("M-UBMC", MOVEMENT_OPTIONS),
                    'm_lbmc': st.selectbox("M-LBMC", MOVEMENT_OPTIONS)
                })

            submitted = st.form_submit_button("Add Entry")
            
            if submitted:
                new_entry = create_new_entry(form_data)
                new_entry_df = pd.DataFrame([new_entry])
                st.session_state.manual_entries = pd.concat([st.session_state.manual_entries, new_entry_df], ignore_index=True)
                st.success("Entry added successfully!")

    # Combine uploaded and manual data
    df = combine_data(uploaded_file, st.session_state.manual_entries)

    if df is not None:
        # Apply thresholds and scores using session state thresholds
        scored_df = apply_thresholds(df, st.session_state.thresholds_df)
        
        # Get unique athletes and sports
        athletes = sorted(df['Athlete Name'].unique())
        sports = sorted(df['Sport'].unique())
        
        # Create selection widgets
        col1, col2 = st.columns(2)
        with col1:
            selected_athlete = st.selectbox("Select Athlete", athletes)
        with col2:
            selected_sport = st.selectbox("Select Sport", sports)
        
        # Filter data based on selection
        filtered_df = scored_df[
            (scored_df['Athlete Name'] == selected_athlete) & 
            (scored_df['Sport'] == selected_sport)
        ].sort_values('Test Date')
        
        if not filtered_df.empty:
            st.header("Performance Scores")
            score_cols = [col for col in filtered_df.columns if col.endswith('_Score')]
            if score_cols:
                st.dataframe(
                    filtered_df[['Test Date'] + PERFORMANCE_METRICS + MOVEMENT_METRICS+ score_cols],
                    use_container_width=True
                )
            
            st.header("Performance Metrics Progress")
            for metric in PERFORMANCE_METRICS:
                fig = create_performance_chart(filtered_df, metric)
                st.plotly_chart(fig, use_container_width=True)
            
            st.header("Movement Assessment Progress")
            fig = create_movement_assessment_chart(filtered_df)
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.warning("No data available for the selected athlete and sport combination.")

elif page == "Thresholds Management":
    st.title("Performance Thresholds Management")
    st.markdown("Edit the thresholds directly in the table below. Changes will be automatically saved.")
    
    # Add New Row section
    with st.expander("Add New Threshold"):
        with st.form("new_threshold_form"):
            new_metric = st.selectbox("Select Metric", list(DEFAULT_THRESHOLDS.keys()))
            new_score = st.selectbox("Score", ["Poor", "Fair", "Good", "Excellent"])
            new_min = st.number_input("Minimum Value", format="%.2f")
            new_max = st.text_input("Maximum Value (use '∞' for infinity)")
            
            submit_new = st.form_submit_button("Add Threshold")
            if submit_new:
                new_row = pd.DataFrame([{
                    'Metric': new_metric,
                    'Score': new_score,
                    'Min': new_min,
                    'Max': new_max
                }])
                st.session_state.thresholds_df = pd.concat([st.session_state.thresholds_df, new_row], ignore_index=True)
                st.success("New threshold added successfully!")
    
    # Display editable thresholds with delete button configuration
    thresholds_df = st.session_state.thresholds_df.copy()
    # Add Delete column if it doesn't exist
    if 'Delete' not in thresholds_df.columns:
        thresholds_df['Delete'] = False

    edited_df = st.data_editor(
        thresholds_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Metric": st.column_config.Column(
                "Metric",
                width="medium",
                required=True,
            ),
            "Score": st.column_config.Column(
                "Score",
                width="small",
                required=True,
            ),
            "Min": st.column_config.NumberColumn(
                "Min",
                width="small",
                required=True,
                format="%.2f"
            ),
            "Max": st.column_config.Column(
                "Max",
                width="small",
                required=True,
            ),
            "Delete": st.column_config.CheckboxColumn(
                "Delete",
                help="Select rows to delete",
                default=False,
            ),
        },
        num_rows="dynamic"
    )
    
    # Add delete button and handle deletion
    if st.button("Delete Selected Rows"):
        rows_to_delete = edited_df['Delete'] == True
        if any(rows_to_delete):
            edited_df = edited_df[~rows_to_delete].drop(columns=['Delete'])
            st.session_state.thresholds_df = edited_df
            st.success("Selected rows deleted successfully!")
            st.rerun()
        else:
            st.warning("No rows selected for deletion")
    
    # Update session state if changes are made
    if 'Delete' in edited_df.columns:
        edited_df = edited_df.drop(columns=['Delete'])
    
    if not edited_df.equals(st.session_state.thresholds_df):
        st.session_state.thresholds_df = edited_df
        st.success("Thresholds updated successfully!")