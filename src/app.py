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



    try:
        threshold_df = pd.read_csv("data/notignore/threshold.csv")
        
        # Drop duplicates based only on the "Code" column, keeping the first Test Name associated
        test_name_code_df = threshold_df.drop_duplicates(subset=["Code"])[["Code", "Test Name"]]
        
        st.subheader("Available Tests (Code and Name)")
        if not test_name_code_df.empty:
            st.dataframe(test_name_code_df, use_container_width=True)
        else:
            st.write("No test codes found.")
    except Exception as e:
        st.error(f"Error loading threshold data: {e}")


elif page == "Thresholds Management":
    st.title("Performance Thresholds Management")
    st.markdown("Edit the thresholds directly in the table below. Changes will be automatically saved.")
