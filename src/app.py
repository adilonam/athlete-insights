import streamlit as st
import pandas as pd
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Athlete Insights",
    page_icon="🏃",
    layout="wide"
)

# Title and description
st.title("Athlete Insights Dashboard")
st.markdown("Welcome to the Athlete Insights Dashboard. Analyze and visualize athlete performance data.")

# Sidebar
st.sidebar.header("Analysis Options")

# Sample data (you can replace this with your actual data)
if 'data' not in st.session_state:
    # Create sample data
    st.session_state.data = pd.DataFrame({
        'Athlete': ['John Doe', 'Jane Smith', 'Mike Johnson'],
        'Sport': ['Running', 'Swimming', 'Cycling'],
        'Performance Score': [85, 92, 78],
        'Training Hours': [120, 150, 100]
    })

# Display data
st.subheader("Athletes Overview")
st.dataframe(st.session_state.data)

# Basic statistics
st.subheader("Performance Statistics")
col1, col2 = st.columns(2)

with col1:
    st.metric("Average Performance Score", 
              f"{st.session_state.data['Performance Score'].mean():.1f}")

with col2:
    st.metric("Total Training Hours", 
              f"{st.session_state.data['Training Hours'].sum()}")

# Add data visualization
st.subheader("Performance by Sport")
sport_performance = st.session_state.data.groupby('Sport')['Performance Score'].mean()
st.bar_chart(sport_performance)