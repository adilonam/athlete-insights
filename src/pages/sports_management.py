import streamlit as st
import pandas as pd
import os

st.title("Sports Management")
st.markdown("Add, edit, or remove sports from the system. Changes will be saved to the sports database.")

# Define the path to the sports CSV file
SPORTS_CSV_PATH = "./data/notignore/sports.csv"

try:
    # Attempt to load existing sports data
    if os.path.exists(SPORTS_CSV_PATH):
        sports_df = pd.read_csv(SPORTS_CSV_PATH)
    else:
        # Create a new DataFrame if file doesn't exist
        sports_df = pd.DataFrame(columns=["Name"])
        st.warning(f"Sports data file not found at {SPORTS_CSV_PATH}. A new one will be created.")
except Exception as e:
    st.error(f"Error loading sports data: {e}")
    sports_df = pd.DataFrame(columns=["Name"])

# Use Streamlit's data editor for interactive editing
st.markdown("### Edit Sports")
st.markdown("Add new sports or edit existing ones directly in the table below.")

# Show data editor with dynamic rows
edited_sports_df = st.data_editor(
    sports_df, 
    use_container_width=True,
    num_rows="dynamic",
    key="sports_editor",
    column_config={
        "Name": st.column_config.TextColumn(
            "Sport Name",
            help="Name of the sport",
            max_chars=50,
            validate="^[A-Za-z][A-Za-z0-9 ()-]*$"
        )
    },
    hide_index=True
)

# Save changes button
if st.button("Save Changes"):
    try:
        # Validate the data (no empty sport names)
        if edited_sports_df.empty or edited_sports_df["Name"].isnull().any() or (edited_sports_df["Name"] == "").any():
            st.error("Error: Sport names cannot be empty. Please provide valid names for all sports.")
        else:
            # Remove any duplicate sport names (case insensitive)
            edited_sports_df["Name"] = edited_sports_df["Name"].str.strip()
            edited_sports_df = edited_sports_df.drop_duplicates(subset=["Name"], keep="first", ignore_index=True)
            
            # Sort alphabetically
            edited_sports_df = edited_sports_df.sort_values(by="Name").reset_index(drop=True)
            
            # Save to CSV file
            edited_sports_df.to_csv(SPORTS_CSV_PATH, index=False)
            st.success("Sports list updated successfully!")
    except Exception as e:
        st.error(f"Error saving sports data: {e}")
