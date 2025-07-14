# Final updated version including percentile/z-score toggle button
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Password protection
PASSWORD = "cowboy"
st.title("⚽ Radar Chart Explorer")
pwd = st.text_input("Enter password:", type="password")
if pwd != PASSWORD:
    st.warning("Please enter the correct password to access the app.")
    st.stop()

# Define color groups
group_colors = {
    'Off The Ball': 'crimson',
    'Attacking': 'royalblue',
    'Possession': 'seagreen',
    'Defensive': 'darkorange'
}

# Metric definitions (truncated for brevity, you will insert the full dictionary here)
position_metrics = { ... }  # Use your full dictionary here

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
    z_scores_df = (percentile_df - 50) / 15

    plot_data = pd.concat([
        df[['Player', 'Team', 'Age', 'Height']],
        metrics_df,
        percentile_df.add_suffix(' (percentile)'),
        z_scores_df.add_suffix(' (z)')
    ], axis=1)

    selected_player = st.selectbox("Choose a player", plot_data['Player'].dropna().unique().tolist())
    value_type = st.radio("Display chart as:", ["Percentile", "Z Score"])

    def plot_radial_bar(player_name):
        row = plot_data[plot_data['Player'] == player_name]
        selected_metrics = list(metric_groups.keys())
        raw_vals = row[selected_metrics].values.flatten()

        if value_type == "Z Score":
            display_vals = row[[m + ' (z)' for m in selected_metrics]].values.flatten() * 15 + 50
        else:
            display_vals = row[[m + ' (percentile)' for m in selected_metrics]].values.flatten()

        groups = [metric_groups[m] for m in selected_metrics]
        colors = [group_colors[g] for g in groups]
        angles = np.linspace(0, 2 * np.pi, len(selected_metrics), endpoint=False)

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_ylim(0, 100)
        ax.set_yticklabels([])
        ax.set_xticks([])
        ax.spines['polar'].set_visible(False)

        ax.bar(angles, display_vals, width=2*np.pi/len(selected_metrics)*0.9, color=colors, edgecolor=colors, alpha=0.75)

        for i, (angle, raw_val) in enumerate(zip(angles, raw_vals)):
            ax.text(angle, 50, f'{raw_val:.2f}', ha='center', va='center', color='black', fontsize=10, fontweight='bold')

        for i, angle in enumerate(angles):
            label = selected_metrics[i].replace(' per 90', '').replace(', %', ' (%)')
            ax.text(angle, 108, label, ha='center', va='center', color='black', fontsize=10, fontweight='bold')

        for group, group_angles in {g: [a for m, a in zip(selected_metrics, angles) if metric_groups[m] == g] for g in set(groups)}.items():
            ax.text(np.mean(group_angles), 125, group, ha='center', va='center', fontsize=20, fontweight='bold', color=group_colors[group])

        age = row['Age'].values[0]
        height = row['Height'].values[0]
        team = row['Team'].values[0]
        age_str = f"{int(age)} years old" if not pd.isnull(age) else ""
        height_str = f"{int(height)} cm" if not pd.isnull(height) else ""
        ax.set_title(f"{player_name} – {age_str} – {height_str}\n{team}", color='black', size=22, pad=20, y=1.12)

        st.pyplot(fig)

    if selected_player:
        plot_radial_bar(selected_player)

    # Z-score table
    st.markdown("### Players Ranked by Z-Score")
    selected_metrics = list(metric_groups.keys())
    percentiles_all = plot_data[[m + ' (percentile)' for m in selected_metrics]]
    z_scores_all = (percentiles_all - 50) / 15

    plot_data['Avg Z Score'] = z_scores_all.mean(axis=1)
    z_ranking = plot_data[['Player', 'Team', 'Avg Z Score']].dropna().sort_values(by='Avg Z Score', ascending=False)
    st.dataframe(z_ranking.reset_index(drop=True))
