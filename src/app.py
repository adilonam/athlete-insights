import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="Athlete Insights",
    page_icon="🏃",
    layout="wide"
)

# Title and description
st.title("Athlete Insights Dashboard")
st.markdown("Welcome to the Athlete Insights Dashboard. Analyze and visualize athlete performance data.")

# File uploader
uploaded_file = st.file_uploader("Upload Athlete Data CSV", type=['csv'])

if uploaded_file is not None:
    # Read the CSV data
    df = pd.read_csv(uploaded_file)
    
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
    filtered_df = df[(df['Athlete Name'] == selected_athlete) & (df['Sport'] == selected_sport)].sort_values('Test Date')
    print(filtered_df)
    
    if not filtered_df.empty:
        # Performance metrics
        performance_metrics = ['0-10 Yard Sprint (s)', 'Fly-10 (s)', 'Pro-Agility (s)', 
                             'MTP Peak Force (N)', 'Chin-Up Strength (Reps)', 'CMJ (in)', 
                             'NCMJ (in)', 'Seated Med Ball Throw (ft)', '5-Jump RSI']
        
        # Movement assessment metrics
        movement_metrics = ['M-OHS', 'M-HS', 'M-IL', 'M-SM', 'M-ASLR', 
                          'M-TSPU', 'M-RS', 'M-UBMC', 'M-LBMC']
        
        st.header("Performance Metrics Progress")
        # Create performance metric charts
        for metric in performance_metrics:
            fig = px.line(filtered_df, x='Test Date', y=metric, 
                         title=f"{metric} Progress Over Time",
                         markers=True)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.header("Movement Assessment Progress")
        # Create movement assessment charts
        movement_data = filtered_df[['Test Date'] + movement_metrics].melt(
            id_vars=['Test Date'], 
            value_vars=movement_metrics,
            var_name='Movement Assessment',
            value_name='Status'
        )
        
        fig = px.scatter(movement_data, x='Test Date', y='Movement Assessment',
                        color='Status', title="Movement Assessment Progress",
                        height=600)
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.warning("No data available for the selected athlete and sport combination.")