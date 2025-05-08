import pandas as pd
import plotly.express as px

# Constants
PERFORMANCE_METRICS = [
    '0-10 Yard Sprint (s)', 'Fly-10 (s)', 'Pro-Agility (s)',
    'MTP Peak Force (N)', 'Chin-Up Strength (Reps)', 'CMJ (in)',
    'NCMJ (in)', 'Seated Med Ball Throw (ft)', '5-Jump RSI'
]

MOVEMENT_METRICS = [
    'M-OHS', 'M-HS', 'M-IL', 'M-SM', 'M-ASLR',
    'M-TSPU', 'M-RS', 'M-UBMC', 'M-LBMC'
]

MOVEMENT_OPTIONS = ["Pass", "Needs Work"]

def create_new_entry(form_data):
    """Create a new entry dictionary from form data."""
    return {
        'Athlete Name': form_data['athlete_name'],
        'Test Date': form_data['test_date'].strftime('%Y-%m-%d'),
        'Sport': form_data['sport'],
        '0-10 Yard Sprint (s)': form_data['sprint_10'],
        'Fly-10 (s)': form_data['fly_10'],
        'Pro-Agility (s)': form_data['pro_agility'],
        'MTP Peak Force (N)': form_data['mtp_force'],
        'Chin-Up Strength (Reps)': form_data['chin_up'],
        'CMJ (in)': form_data['cmj'],
        'NCMJ (in)': form_data['ncmj'],
        'Seated Med Ball Throw (ft)': form_data['med_ball'],
        '5-Jump RSI': form_data['rsi'],
        'M-OHS': form_data['m_ohs'],
        'M-HS': form_data['m_hs'],
        'M-IL': form_data['m_il'],
        'M-SM': form_data['m_sm'],
        'M-ASLR': form_data['m_aslr'],
        'M-TSPU': form_data['m_tspu'],
        'M-RS': form_data['m_rs'],
        'M-UBMC': form_data['m_ubmc'],
        'M-LBMC': form_data['m_lbmc']
    }

def combine_data(uploaded_file, manual_entries):
    """Combine uploaded CSV data with manual entries."""
    if uploaded_file is not None:
        uploaded_df = pd.read_csv(uploaded_file)
        if not manual_entries.empty:
            return pd.concat([uploaded_df, manual_entries], ignore_index=True)
        return uploaded_df
    elif not manual_entries.empty:
        return manual_entries
    return None

def create_performance_chart(filtered_df, metric):
    """Create a performance metric chart."""
    fig = px.line(filtered_df, x='Test Date', y=metric,
                  title=f"{metric} Progress Over Time",
                  markers=True)
    fig.update_layout(height=400)
    return fig

def create_movement_assessment_chart(filtered_df):
    """Create movement assessment chart."""
    movement_data = filtered_df[['Test Date'] + MOVEMENT_METRICS].melt(
        id_vars=['Test Date'],
        value_vars=MOVEMENT_METRICS,
        var_name='Movement Assessment',
        value_name='Status'
    )
    
    fig = px.scatter(movement_data, x='Test Date', y='Movement Assessment',
                    color='Status', title="Movement Assessment Progress",
                    height=600)
    return fig