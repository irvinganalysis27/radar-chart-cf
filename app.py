import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- Basic password protection ---
PASSWORD = "cowboy"

st.title("⚽ Radar Chart Explorer")

pwd = st.text_input("Enter password:", type="password")
if pwd != PASSWORD:
    st.warning("Please enter the correct password to access the app.")
    st.stop()

# --- Metric Sets for Positions ---
position_metrics = {
    "Penalty Box CB": {
        "metrics": [
            'Defensive duels per 90', 'Defensive duels won, %', 'Aerial duels per 90',
            'Aerial duels won, %', 'Shots blocked per 90', 'PAdj Interceptions',
            'Head goals per 90', 'Successful dribbles, %', 'Accurate passes, %'
        ],
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
    z_df = (percentile_df - 50) / 15
    z_df = z_df.round(2)

    # Combine
    plot_data = pd.concat([
        df[['Player', 'Team', 'Age', 'Height']],
        metrics_df,
        percentile_df.add_suffix(' (percentile)'),
        z_df.add_suffix(' (z)')
    ], axis=1)

    players = plot_data['Player'].dropna().unique().tolist()
    selected_player = st.selectbox("Choose a player", players)
    view_option = st.radio("Choose data display", ["Percentile", "Z-Score"])

    def plot_radial(player_name, plot_data, metric_groups, group_colors, use_z_score=False):
        row = plot_data[plot_data['Player'] == player_name]
        selected_metrics = list(metric_groups.keys())

        if use_z_score:
            values = row[[m + ' (z)' for m in selected_metrics]].values.flatten()
            y_limit = (-3, 3)
        else:
            values = row[[m + ' (percentile)' for m in selected_metrics]].values.flatten()
            y_limit = (0, 100)

        raw = row[selected_metrics].values.flatten()
        groups = [metric_groups[m] for m in selected_metrics]
        colors = [group_colors[g] for g in groups]
        angles = np.linspace(0, 2 * np.pi, len(selected_metrics), endpoint=False)

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_ylim(*y_limit)
        ax.set_yticklabels([])
        ax.set_xticks([])
        ax.spines['polar'].set_visible(False)

        ax.bar(angles, values, width=2 * np.pi / len(selected_metrics) * 0.9,
               color=colors, edgecolor=colors, alpha=0.75)

        for i, (angle, raw_val) in enumerate(zip(angles, raw)):
            ax.text(angle, (y_limit[1] + y_limit[0]) / 2, f'{raw_val:.2f}',
                    ha='center', va='center', color='black', fontsize=10, fontweight='bold')

        for i, angle in enumerate(angles):
            label = selected_metrics[i].replace(' per 90', '').replace(', %', ' (%)')
            ax.text(angle, y_limit[1] + 5, label, ha='center', va='center',
                    color='black', fontsize=10, fontweight='bold')

        group_positions = {}
        for g, a in zip(groups, angles):
            group_positions.setdefault(g, []).append(a)
        for group, group_angles in group_positions.items():
            mean_angle = np.mean(group_angles)
            ax.text(mean_angle, y_limit[1] + 20, group, ha='center', va='center',
                    fontsize=20, fontweight='bold', color=group_colors[group])

        age = row['Age'].values[0]
        height = row['Height'].values[0]
        team = row['Team'].values[0]
        line1 = f"{player_name} – {int(age)} years old – {int(height)} cm"
        ax.set_title(f"{line1}\n{team}", color='black', size=22, pad=20, y=1.12)

        z_vals = row[[m + ' (z)' for m in selected_metrics]].values.flatten()
        avg_z = np.mean(z_vals)

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
            f"<span style='font-size:24px; font-weight:bold;'>Average Z Score – {avg_z:.2f}</span><br>"
            f"<span style='background-color:{badge[1]}; color:white; padding:5px 10px; border-radius:8px; font-size:20px;'>"
            f"{badge[0]}"
            f"</span></div>",
            unsafe_allow_html=True
        )

        st.pyplot(fig)

    if selected_player:
        plot_radial(selected_player, plot_data, metric_groups, group_colors, use_z_score=(view_option == "Z-Score"))

    # Table
    st.markdown("### Players Ranked by Z-Score")
    selected_metrics = list(metric_groups.keys())
    z_scores_all = plot_data[[m + ' (z)' for m in selected_metrics]]
    plot_data['Avg Z Score'] = z_scores_all.mean(axis=1)
    z_ranking = plot_data[['Player', 'Team', 'Avg Z Score']].dropna().sort_values(by='Avg Z Score', ascending=False)
    st.dataframe(z_ranking.reset_index(drop=True))
