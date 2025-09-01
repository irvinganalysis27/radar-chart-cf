import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

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
            "Passes to final third per 90": "Possession",
            "Accurate passes to final third, %": "Possession"
            "xA per 90": "Attacking"
            "Assists per 90": "Attacking"

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
    },
    "Creative CM": {
        "metrics": [
            "Non-penalty goals per 90", "xG per 90", "Goal conversion, %",
            "Assists per 90", "xA per 90", "Shots per 90", "Shots on target, %",
            "Forward passes per 90", "Accurate forward passes, %",
            "Through passes per 90", "Accurate through passes, %",
            "Dribbles per 90", "Successful dribbles, %"
        ],
        "groups": {
            "Non-penalty goals per 90": "Attacking",
            "xG per 90": "Attacking",
            "Goal conversion, %": "Attacking",
            "Assists per 90": "Attacking",
            "xA per 90": "Attacking",
            "Shots per 90": "Attacking",
            "Shots on target, %": "Attacking",
            "Forward passes per 90": "Possession",
            "Accurate forward passes, %": "Possession",
            "Through passes per 90": "Possession",
            "Accurate through passes, %": "Possession",
            "Dribbles per 90": "Possession",
            "Successful dribbles, %": "Possession"
        }
    }
}

# Colors
group_colors = {
    'Off The Ball': 'crimson',
    'Attacking': 'royalblue',
    'Possession': 'seagreen',
    'Defensive': 'darkorange'
}

# File upload
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # --- Minutes filtering, no dropdown ---
    minutes_col = "Minutes played"  # hard coded
    min_minutes = st.number_input("Minimum minutes to include", min_value=0, value=1000, step=50)

    df["_minutes_numeric"] = pd.to_numeric(df[minutes_col], errors="coerce")
    df_filtered = df[df["_minutes_numeric"] >= min_minutes].copy()

    if df_filtered.empty:
        st.warning("No players meet the minutes threshold. Lower the minimum.")
        st.stop()

    st.caption(f"Filtering on '{minutes_col}' with threshold {min_minutes}. Players remaining: {len(df_filtered)}")

    selected_position = st.selectbox("Choose a position", list(position_metrics.keys()))
    metrics = position_metrics[selected_position]["metrics"]
    metric_groups = position_metrics[selected_position]["groups"]

    # Ensure all required metric columns exist
    for m in metrics:
        if m not in df_filtered.columns:
            df_filtered[m] = 0

    df_filtered[metrics] = df_filtered[metrics].fillna(0)
    metrics_df = df_filtered[metrics]
    percentile_df = metrics_df.rank(pct=True) * 100
    percentile_df = percentile_df.round(1)

    # Include both team columns
    plot_data = pd.concat([
        df_filtered[['Player', 'Team within selected timeframe', 'Team', 'Age', 'Height']],
        metrics_df,
        percentile_df.add_suffix(' (percentile)')
    ], axis=1)

    players = plot_data['Player'].dropna().unique().tolist()
    selected_player = st.selectbox("Choose a player", players)

    def plot_radial_bar_grouped(player_name, plot_data, metric_groups, group_colors):
        row = plot_data[plot_data['Player'] == player_name]
        if row.empty:
            st.error(f"No player named '{player_name}' found.")
            return

        selected_metrics = list(metric_groups.keys())
        raw = row[selected_metrics].values.flatten()
        percentiles = row[[m + ' (percentile)' for m in selected_metrics]].values.flatten()
        groups = [metric_groups[m] for m in selected_metrics]
        colors = [group_colors[g] for g in groups]

        num_bars = len(selected_metrics)
        angles = np.linspace(0, 2 * np.pi, num_bars, endpoint=False)

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_ylim(0, 100)
        ax.set_yticklabels([])
        ax.set_xticks([])
        ax.spines['polar'].set_visible(False)

        ax.bar(angles, percentiles, width=2*np.pi/num_bars * 0.9,
               color=colors, edgecolor=colors, alpha=0.75)

        for angle, raw_val in zip(angles, raw):
            ax.text(angle, 50, f'{raw_val:.2f}', ha='center', va='center',
                    color='black', fontsize=10, fontweight='bold', rotation=0)

        for i, angle in enumerate(angles):
            label = selected_metrics[i].replace(' per 90', '').replace(', %', ' (%)')
            ax.text(angle, 108, label, ha='center', va='center', rotation=0,
                    color='black', fontsize=10, fontweight='bold')

        group_positions = {}
        for g, a in zip(groups, angles):
            group_positions.setdefault(g, []).append(a)
        for group, group_angles in group_positions.items():
            mean_angle = np.mean(group_angles)
            ax.text(mean_angle, 125, group, ha='center', va='center',
                    fontsize=20, fontweight='bold', color=group_colors[group], rotation=0)

        age = row['Age'].values[0]
        height = row['Height'].values[0]
        team = row['Team within selected timeframe'].values[0]
        age_str = f"{int(age)} years old" if not pd.isnull(age) else ""
        height_str = f"{int(height)} cm" if not pd.isnull(height) else ""
        parts = [player_name]
        if age_str: parts.append(age_str)
        if height_str: parts.append(height_str)
        line1 = " | ".join(parts)
        line2 = f"{team}" if pd.notnull(team) else ""
        ax.set_title(f"{line1}\n{line2}", color='black', size=22, pad=20, y=1.12)

        z_scores = (percentiles - 50) / 15
        avg_z = np.mean(z_scores)

        if avg_z >= 1.0:
            badge = ("Excellent", "#228B22")
        elif avg_z >= 0.3:
            badge = ("Good", "#1E90FF")
        elif avg_z >= -0.3:
            badge = ("Average", "#DAA520")
        else:
            badge = ("Below Average", "#DC143C")

        st.markdown(
            f"<div style='text-align:center; margin-top: 20px;'>"
            f"<span style='font-size:24px; font-weight:bold;'>Average Z Score, {avg_z:.2f}</span><br>"
            f"<span style='background-color:{badge[1]}; color:white; padding:5px 10px; border-radius:8px; font-size:20px;'>"
            f"{badge[0]}"
            f"</span></div>",
            unsafe_allow_html=True
        )

        st.pyplot(fig)

    if selected_player:
        plot_radial_bar_grouped(selected_player, plot_data, metric_groups, group_colors)

    st.markdown("### Players Ranked by Z-Score")
    selected_metrics = list(metric_groups.keys())
    percentiles_all = plot_data[[m + ' (percentile)' for m in selected_metrics]]
    z_scores_all = (percentiles_all - 50) / 15
    plot_data['Avg Z Score'] = z_scores_all.mean(axis=1)

    z_ranking = (
        plot_data[['Player', 'Age', 'Team', 'Team within selected timeframe', 'Avg Z Score']]
        .sort_values(by='Avg Z Score', ascending=False)
    )
    z_ranking[['Team', 'Team within selected timeframe']] = (
        z_ranking[['Team', 'Team within selected timeframe']].fillna("N/A")
    )
    z_ranking['Age'] = z_ranking['Age'].apply(lambda x: int(x) if pd.notnull(x) else x)

    z_ranking.insert(0, 'Rank', range(1, len(z_ranking) + 1))
    z_ranking = z_ranking.set_index('Rank')

    st.dataframe(z_ranking)
