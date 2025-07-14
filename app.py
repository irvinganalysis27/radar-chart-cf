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

group_colors = {
    'Off The Ball': 'crimson',
    'Attacking': 'royalblue',
    'Possession': 'seagreen',
    'Defensive': 'darkorange'
}

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    selected_position = st.selectbox("Choose a position", list(position_metrics.keys()))
    metrics = position_metrics[selected_position]["metrics"]
    metric_groups = position_metrics[selected_position]["groups"]

    df[metrics] = df[metrics].fillna(0)
    metrics_df = df[metrics]
    percentile_df = metrics_df.rank(pct=True) * 100
    percentile_df = percentile_df.round(1)
    z_score_df = (percentile_df - 50) / 15

    plot_data = pd.concat([
        df[['Player', 'Team', 'Age', 'Height']],
        metrics_df,
        percentile_df.add_suffix(' (percentile)'),
        z_score_df.add_suffix(' (z-score)')
    ], axis=1)

    players = plot_data['Player'].dropna().unique().tolist()
    selected_player = st.selectbox("Choose a player", players)

    display_option = st.radio("Select chart display", ["Percentiles", "Z-scores"])

    def plot_radial(player_name, data, group_map, group_colors, display_type):
        row = data[data['Player'] == player_name]
        selected_metrics = list(group_map.keys())
        values = row[[m + (' (percentile)' if display_type == 'Percentiles' else ' (z-score)') for m in selected_metrics]].values.flatten()
        groups = [group_map[m] for m in selected_metrics]
        colors = [group_colors[g] for g in groups]

        angles = np.linspace(0, 2*np.pi, len(selected_metrics), endpoint=False)
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_ylim(0 if display_type == "Percentiles" else -3, 100 if display_type == "Percentiles" else 3)
        ax.set_yticklabels([])
        ax.set_xticks([])
        ax.spines['polar'].set_visible(False)

        ax.bar(angles, values, width=2*np.pi/len(selected_metrics) * 0.9, color=colors, edgecolor=colors, alpha=0.75)

        for i, angle in enumerate(angles):
            label = selected_metrics[i].replace(' per 90', '').replace(', %', ' (%)')
            ax.text(angle, ax.get_ylim()[1] + 5, label, ha='center', va='center', rotation=0, fontsize=10, fontweight='bold')

        mean_angle = {g: np.mean([a for i, a in enumerate(angles) if groups[i] == g]) for g in set(groups)}
        for g, a in mean_angle.items():
            ax.text(a, ax.get_ylim()[1] + 20, g, ha='center', va='center', fontsize=20, fontweight='bold', color=group_colors[g])

        age = row['Age'].values[0]
        height = row['Height'].values[0]
        team = row['Team'].values[0]
        title = f"{player_name} – {int(age)} years old – {int(height)} cm\n{team}"
        ax.set_title(title, size=22, y=1.12)

        st.pyplot(fig)

    if selected_player:
        plot_radial(selected_player, plot_data, metric_groups, group_colors, display_option)

    # Z-score table
    st.markdown("### Players Ranked by Z-Score")
    selected_metrics = list(metric_groups.keys())
    percentiles_all = plot_data[[m + ' (percentile)' for m in selected_metrics]]
    z_scores_all = (percentiles_all - 50) / 15
    plot_data['Avg Z Score'] = z_scores_all.mean(axis=1)
    z_ranking = plot_data[['Player', 'Team', 'Avg Z Score']].dropna().sort_values(by='Avg Z Score', ascending=False)
    st.dataframe(z_ranking.reset_index(drop=True))
