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

# --- Radar Chart Function ---
def plot_radial_bar_grouped(player_name, plot_data, metric_groups, group_colors):
    row = plot_data[plot_data['Player'] == player_name]
    if row.empty:
        st.error(f"No player named '{player_name}' found.")
        return

    selected_metrics = list(metric_groups.keys())
    raw = row[selected_metrics].fillna(0).values.flatten()
    percentiles = row[[m + ' (percentile)' for m in selected_metrics]].fillna(0).values.flatten()
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

    # Bars
    ax.bar(angles, percentiles, width=2*np.pi/num_bars * 0.9,
           color=colors, edgecolor=colors, alpha=0.75)

    # Raw numbers (fixed halfway)
    for i, (angle, raw_val) in enumerate(zip(angles, raw)):
        ax.text(angle, 50, f'{raw_val:.2f}', ha='center', va='center',
                color='black', fontsize=10, fontweight='bold', rotation=0)

    # Labels
    for i, angle in enumerate(angles):
        label = selected_metrics[i]
        label = label.replace(' per 90', '').replace('Goal conversion, %', 'Conversion (%)')
        label = label.replace('Aerial duels won, %', 'Aerials won (%)')
        label = label.replace('Offensive duels won, %', 'Off. duels won (%)')
        label = label.replace('Successful defensive actions', 'Def. actions')
        ax.text(angle, 108, label, ha='center', va='center', rotation=0,
                color='black', fontsize=10, fontweight='bold')

    # Section headers
    group_positions = {}
    for g, a in zip(groups, angles):
        group_positions.setdefault(g, []).append(a)
    for group, group_angles in group_positions.items():
        mean_angle = np.mean(group_angles)
        ax.text(mean_angle, 125, group, ha='center', va='center',
                fontsize=20, fontweight='bold', color=group_colors[group], rotation=0)

    # Title
    age = row['Age'].values[0]
    height = row['Height'].values[0]
    team = row['Team'].values[0]
    age_str = f"{int(age)} years old" if not pd.isnull(age) else ""
    height_str = f"{int(height)} cm" if not pd.isnull(height) else ""
    line1 = f"{player_name} – {age_str} – {height_str}".strip(" –")
    line2 = f"{team}"
    ax.set_title(f"{line1}\n{line2}", color='black', size=22, pad=20, y=1.12)

    # --- Average Z-score Calculation ---
    z_scores = (percentiles - 50) / 15
    avg_z = np.mean(z_scores)

    # Badge
    if avg_z >= 1.0:
        badge = ("Excellent", "#228B22")
    elif avg_z >= 0.3:
        badge = ("Good", "#1E90FF")
    elif avg_z >= -0.3:
        badge = ("Average", "#DAA520")
    else:
        badge = ("Below Average", "#DC143C")

    # Show score + badge
    st.markdown(
        f"<div style='text-align:center; margin-top: 20px;'>"
        f"<span style='font-size:24px; font-weight:bold;'>Average Z Score – {avg_z:.2f}</span><br>"
        f"<span style='background-color:{badge[1]}; color:white; padding:5px 10px; border-radius:8px; font-size:20px;'>"
        f"{badge[0]}"
        f"</span></div>",
        unsafe_allow_html=True
    )

    st.pyplot(fig)

# --- Streamlit Interface ---
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    metric_cols = df.columns[9:]
    metrics_df = df[metric_cols].fillna(0)
    percentile_df = metrics_df.rank(pct=True) * 100
    percentile_df = percentile_df.round(1)
    plot_data = pd.concat([
        df[['Player', 'Team', 'Age', 'Height']],
        metrics_df,
        percentile_df.add_suffix(' (percentile)')
    ], axis=1)

    # Metric groups
    metric_groups = {
        'Successful defensive actions per 90': 'Off The Ball',
        'Aerial duels per 90': 'Off The Ball',
        'Aerial duels won, %': 'Off The Ball',
        'Non-penalty goals per 90': 'Attacking',
        'xG per 90': 'Attacking',
        'Shots per 90': 'Attacking',
        'Shots on target, %': 'Attacking',
        'Goal conversion, %': 'Attacking',
        'Assists per 90': 'Attacking',
        'xA per 90': 'Attacking',
        'Shot assists per 90': 'Attacking',
        'Offensive duels per 90': 'Possession',
        'Offensive duels won, %': 'Possession'
    }
    group_colors = {
        'Off The Ball': 'crimson',
        'Attacking': 'royalblue',
        'Possession': 'seagreen'
    }

    # --- Player Z Score Table ---
    selected_metrics = list(metric_groups.keys())
    percentile_cols = [m + ' (percentile)' for m in selected_metrics]
    z_df = plot_data[['Player'] + percentile_cols].copy()
    z_df[percentile_cols] = z_df[percentile_cols].fillna(0)
    z_df['Z Score'] = z_df[percentile_cols].apply(lambda row: ((row - 50) / 15).mean(), axis=1)
    z_df_sorted = z_df[['Player', 'Z Score']].sort_values(by='Z Score', ascending=False).reset_index(drop=True)

    st.subheader("📊 Player Z Score Rankings")
    st.dataframe(z_df_sorted)

    # --- Dropdown and Radar ---
    players = plot_data['Player'].dropna().unique().tolist()
    selected_player = st.selectbox("Choose a player", players)

    if selected_player:
        plot_radial_bar_grouped(selected_player, plot_data, metric_groups, group_colors)
