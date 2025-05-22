import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Athlete Insights",
    page_icon="🏃",
    layout="wide"
)

st.title("Athlete Insights")
st.markdown("Welcome to Athlete Insights! Use the sidebar to navigate to different sections.")

# Streamlit will automatically find and run pages from the 'pages' directory.
# No explicit routing is needed here anymore.

# The content of what was previously the default page (main_dashboard) 
# can either be moved here to app.py to serve as the landing page,
# or main_dashboard.py can be renamed to something like 01_Main_Dashboard.py 
# in the pages folder to control its order and make it the default.
# For now, app.py will just show a welcome message.
