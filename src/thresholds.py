import pandas as pd

# Default thresholds for each performance metric
DEFAULT_THRESHOLDS = {
    '0-10 Yard Sprint (s)': {'Poor': (1.8, float('inf')), 'Fair': (1.65, 1.8), 'Good': (1.5, 1.65), 'Excellent': (0, 1.5)},
    'Fly-10 (s)': {'Poor': (1.2, float('inf')), 'Fair': (1.05, 1.2), 'Good': (0.9, 1.05), 'Excellent': (0, 0.9)},
    'Pro-Agility (s)': {'Poor': (4.6, float('inf')), 'Fair': (4.4, 4.6), 'Good': (4.2, 4.4), 'Excellent': (0, 4.2)},
    'MTP Peak Force (N)': {'Poor': (0, 2000), 'Fair': (2000, 2300), 'Good': (2300, 2600), 'Excellent': (2600, float('inf'))},
    'Chin-Up Strength (Reps)': {'Poor': (0, 8), 'Fair': (8, 12), 'Good': (12, 15), 'Excellent': (15, float('inf'))},
    'CMJ (in)': {'Poor': (0, 25), 'Fair': (25, 27), 'Good': (27, 29), 'Excellent': (29, float('inf'))},
    'NCMJ (in)': {'Poor': (0, 23), 'Fair': (23, 25), 'Good': (25, 27), 'Excellent': (27, float('inf'))},
    'Seated Med Ball Throw (ft)': {'Poor': (0, 16), 'Fair': (16, 17.5), 'Good': (17.5, 19), 'Excellent': (19, float('inf'))},
    '5-Jump RSI': {'Poor': (0, 1.9), 'Fair': (1.9, 2.1), 'Good': (2.1, 2.2), 'Excellent': (2.2, float('inf'))}
}

def calculate_score(value, metric, session_state_df=None):
    """Calculate performance score based on thresholds."""
    if session_state_df is not None:
        # Get thresholds from session state DataFrame
        metric_thresholds = session_state_df[session_state_df['Metric'] == metric]
        for _, row in metric_thresholds.iterrows():
            min_val = float(row['Min'])
            max_val = float('inf') if row['Max'] == '∞' else float(row['Max'])
            if min_val <= float(value) < max_val:
                return row['Score']
    else:
        # Fallback to default thresholds
        thresholds = DEFAULT_THRESHOLDS[metric]
        for score, (min_val, max_val) in thresholds.items():
            if min_val <= float(value) < max_val:
                return score
    return 'Unknown'

def get_threshold_df():
    """Convert thresholds to a DataFrame for display and editing."""
    data = []
    for metric, ranges in DEFAULT_THRESHOLDS.items():
        for score, (min_val, max_val) in ranges.items():
            max_val_display = str(max_val) if max_val != float('inf') else '∞'
            data.append({
                'Metric': metric,
                'Score': score,
                'Min': min_val,
                'Max': max_val_display
            })
    return pd.DataFrame(data)

def apply_thresholds(df, session_state_df=None):
    """Apply thresholds to performance metrics and add score columns."""
    scored_df = df.copy()
    for metric in DEFAULT_THRESHOLDS.keys():
        if metric in df.columns:
            scored_df[f'{metric}_Score'] = df[metric].apply(
                lambda x: calculate_score(x, metric, session_state_df)
            )
    return scored_df