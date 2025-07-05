import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- Basic password protection ---
PASSWORD = "cowboy"

st.title("⚽ Radar Chart Explorer")

# Ask for password
pwd = st.text_input("Enter password:", type="password")
if pwd != PASSWORD:
    st.warning("Please enter the correct password to access the app.")
    st.stop()

# --- Metric Sets for Positions ---
position_metrics = {
    "Centre Forward (CF)": {
        "metrics": [
            "Successful defensive actions per 90", "Aerial duels per 90", "Aerial duels won, %",
            "Non-penalty goals per 90", "xG per 90", "Shots per 90", "Shots on target, %",
            "Goal conversion, %", "Assists per 90", "xA per 90", "Shot assists per 90",
            "Offensive duels per 90", "Offensive duels won, %"
        ],
        "groups": {
            "Successful defensive actions per 90": "Off The Ball",
            "Aerial duels per 90": "Off The Ball",
            "Aerial duels won, %": "Off The Ball",
            "Non-penalty goals per 90": "Attacking",
            "xG per 90": "Attacking",
            "Shots per 90": "Attacking",
            "Shots on target, %": "Attacking",
            "Goal conversion, %": "Attacking",
            "Assists per 90": "Attacking",
            "xA per 90": "Attacking",
            "Shot assists per 90": "Attacking",
            "Offensive duels per 90": "Possession",
            "Offensive duels won, %": "Possession"
        }
    },
    "Full Back (FB)": {
        "metrics": [
            "Successful defensive actions per 90", "Defensive duels per 90", "Defensive duels won, %",
            "PAdj Interceptions", "Assists per 90", "Crosses per 90", "Accurate crosses, %",
            "Dribbles per 90", "Successful dribbles, %", "Offensive duels per 90",
            "Offensive duels won, %", "xA per 90", "Passes to final third per 90",
            "Accurate passes to final third, %"
        ],
        "groups": {
            "Successful defensive actions per 90": "Defensive",
            "Defensive duels per 90": "Defensive",
            "Defensive duels won, %": "Defensive",
            "PAdj Interceptions": "Defensive",
            "Crosses per 90": "Possession",
            "Accurate crosses, %": "Possession",
            "Dribbles per 90": "Possession",
            "Successful dribbles, %": "Possession",
            "Offensive duels per 90": "Possession",
            "Offensive duels won, %": "Possession",
            "xA per 90": "Attacking",
            "Assists per 90": "Attacking",
            "Passes to final third per 90": "Possession",
            "Accurate passes to final third, %": "Possession"
        }
    },
    "Destroyer CM": {
        "metrics": [
            "Successful defensive actions per 90", "Defensive duels per 90", "Defensive duels won, %",
            "Aerial duels per 90", "Aerial duels won, %", "PAdj Interceptions", "Successful dribbles, %",
            "Offensive duels per 90", "Offensive duels won, %", "Accurate passes, %",
            "Forward passes per 90", "Accurate forward passes, %", "Passes to final third per 90",
            "Accurate passes to final third, %"
        ],
        "groups": {
            "Successful defensive actions per 90": "Defensive",
            "Defensive duels per 90": "Defensive",
            "Defensive duels won, %": "Defensive",
            "Aerial duels per 90": "Defensive",
            "Aerial duels won, %": "Defensive",
            "PAdj Interceptions": "Defensive",
            "Successful dribbles, %": "Possession",
            "Offensive duels per 90": "Possession",
            "Offensive duels won, %": "Possession",
            "Accurate passes, %": "Possession",
            "Forward passes per 90": "Possession",
            "Accurate forward passes, %": "Possession",
            "Passes to final third per 90": "Possession",
            "Accurate passes to final third, %": "Possession"
        }
    },
    "Penalty Box CB": {
        "metrics": ['Defensive duels per 90', 'Defensive duels won, %', 'Aerial duels per 90',
                    'Aerial duels won, %', 'Shots blocked per 90', 'PAdj Interceptions',
                    'Head goals per 90', 'Successful dribbles, %', 'Accurate passes, %'],
        "groups": {
            'Defensive duels per 90': 'Defensive',
            'Defensive duels won, %': 'Defensive',
            'Aerial duels per 90': 'Defensive',
            'Aerial duels won, %': 'Defensive',
            'Shots blocked per 90': 'Defensive',
            'PAdj Interceptions': 'Defensive',
            'Head goals per 90': 'Possession',
            'Successful dribbles, %': 'Possession',
            'Accurate passes, %': 'Possession'
        }
    },
    "Winger": {
        "metrics": [
            "Non-penalty goals per 90", "xG per 90", "Shots per 90", "Shots on target, %",
            "Goal conversion, %", "Assists per 90", "xA per 90", "Crosses per 90",
            "Accurate crosses, %", "Dribbles per 90", "Successful dribbles, %",
            "Fouls suffered per 90", "Shot assists per 90", "Passes to penalty area per 90",
            "Accurate passes to penalty area, %"
        ],
        "groups": {
            "Non-penalty goals per 90": "Attacking",
            "xG per 90": "Attacking",
            "Shots per 90": "Attacking",
            "Shots on target, %": "Attacking",
            "Goal conversion, %": "Attacking",
            "Assists per 90": "Attacking",
            "xA per 90": "Attacking",
            "Crosses per 90": "Possession",
            "Accurate crosses, %": "Possession",
            "Dribbles per 90": "Possession",
            "Successful dribbles, %": "Possession",
            "Fouls suffered per 90": "Possession",
            "Shot assists per 90": "Possession",
            "Passes to penalty area per 90": "Possession",
            "Accurate passes to penalty area, %": "Possession"
        }
    }
}

# (rest of your app remains unchanged)

# Define group colors
group_colors = {
    'Off The Ball': 'crimson',
    'Attacking': 'royalblue',
    'Possession': 'seagreen',
    'Defensive': 'darkorange'
}

# The rest of the app logic stays as-is from your last version
