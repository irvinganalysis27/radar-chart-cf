import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Basic password protection ---
PASSWORD = "cowboy"

st.title("⚽ Radar Chart Explorer")

# Ask for password
pwd = st.text_input("Enter password:", type="password")
if pwd != PASSWORD:
    st.warning("Please enter the correct password to access the app.")
    st.stop()

# Define group colors
group_colors = {
    'Off The Ball': 'crimson',
    'Attacking': 'royalblue',
    'Possession': 'seagreen',
    'Defensive': 'darkorange'
}

# --- Toggle Display Mode ---
display_mode = st.radio("Choose chart type", ["Percentile", "Z-Score"])

# --- Metric Sets for Positions ---
# [Define your `position_metrics` dictionary here — unchanged for brevity]

# --- Upload and Process File ---
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

    # Add Z-scores
    z_scores_df = (percentile_df - 50) / 15  # Z-score from percentile

    plot_data = pd.concat([
        df[['Player', 'Team', 'Age', 'Height']],
        metrics_df,
        percentile_df.add_suffix(' (percentile)'),
        z_scores_df.add_suffix(' (z-score)')
    ], axis=1)

    players = plot_data['Player'].dropna().unique().tolist()
    selected_player = st.selectbox("Choose a player", players)

    def plot_radial_bar_grouped(player_name, plot_data, metric_groups, group_colors, display_mode):
        row = plot_data[plot_data['Player'] == player_name]
        if row.empty:
            st.error(f"No player named '{player_name}' found.")
            return

        selected_metrics = list(metric_groups.keys())
        raw = row[selected_metrics].values.flatten()
        percentiles = row[[m + ' (percentile)' for m in selected_metrics]].values.flatten()
        z_scores = row[[m + ' (z-score)' for m in selected_metrics]].values.flatten()
        groups = [metric_groups[m] for m in selected_metrics]
        colors = [group_colors[g] for g in groups]

        # Scale for visualisation
        if display_mode == "Percentile":
            bars = percentiles
            radial_limit = 100
        else:
            bars = (z_scores + 3) / 6 * 100  # Normalize -3 to +3 z-scores to 0–100
            radial_limit = 100

        angles = np.linspace(0, 2 * np.pi, len(selected_metrics), endpoint=False)

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_ylim(0, radial_limit)
        ax.set_yticklabels([])
        ax.set_xticks([])
        ax.spines['polar'].set_visible(False)

        ax.bar(angles, bars, width=2*np.pi/len(selected_metrics) * 0.9,
               color=colors, edgecolor=colors, alpha=0.75)

        for i, (angle, raw_val) in enumerate(zip(angles, raw)):
            ax.text(angle, 50, f'{raw_val:.2f}', ha='center', va='center',
                    color='black', fontsize=10, fontweight='bold')

        for i, angle in enumerate(angles):
            label = selected_metrics[i].replace(' per 90', '').replace(', %', ' (%)')
            ax.text(angle, radial_limit + 8, label, ha='center', va='center',
                    color='black', fontsize=10, fontweight='bold')

        group_positions = {}
        for g, a in zip(groups, angles):
            group_positions.setdefault(g, []).append(a)
        for group, group_angles in group_positions.items():
            mean_angle = np.mean(group_angles)
            ax.text(mean_angle, radial_limit + 25, group, ha='center', va='center',
                    fontsize=20, fontweight='bold', color=group_colors[group])

        age = row['Age'].values[0]
        height = row['Height'].values[0]
        team = row['Team'].values[0]
        line1 = f"{player_name} – {int(age)} years old – {int(height)} cm"
        line2 = f"{team}"
        ax.set_title(f"{line1}\n{line2}", color='black', size=22, pad=20, y=1.12)

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
            f"<span style='font-size:24px; font-weight:bold;'>Average Z Score – {avg_z:.2f}</span><br>"
            f"<span style='background-color:{badge[1]}; color:white; padding:5px 10px; border-radius:8px; font-size:20px;'>"
            f"{badge[0]}"
            f"</span></div>",
            unsafe_allow_html=True
        )

        st.pyplot(fig)

    if selected_player:
        plot_radial_bar_grouped(
            selected_player, plot_data, metric_groups, group_colors, display_mode
        )

    # Show ranked Z-score table
    st.markdown("### Players Ranked by Z-Score")
    selected_metrics = list(metric_groups.keys())
    percentiles_all = plot_data[[m + ' (percentile)' for m in selected_metrics]]
    z_scores_all = (percentiles_all - 50) / 15
    plot_data['Avg Z Score'] = z_scores_all.mean(axis=1)
    z_ranking = plot_data[['Player', 'Team', 'Avg Z Score']].dropna().sort_values(by='Avg Z Score', ascending=False)
    st.dataframe(z_ranking.reset_index(drop=True))
