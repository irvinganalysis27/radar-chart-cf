import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- Password gate ---
PASSWORD = "cowboy"

st.set_page_config(page_title="Radar Chart", layout="wide")
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("Enter password", type="password")
    if password == PASSWORD:
        st.session_state.authenticated = True
    else:
        st.stop()

# --- Define radar chart function ---
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

    # Bars
    bars = ax.bar(angles, percentiles, width=2*np.pi/num_bars * 0.9,
                  color=colors, edgecolor=colors, alpha=0.75)

    # Raw numbers
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

    st.pyplot(fig)

# --- Streamlit Interface ---
st.title("⚽ Radar Chart Explorer")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Fill missing metric values with 0
    df.fillna(0, inplace=True)

    metric_cols = df.columns[9:]
    metrics_df = df[metric_cols]
    percentile_df = metrics_df.rank(pct=True) * 100
    percentile_df = percentile_df.round(1)
    z_scores_df = ((metrics_df - metrics_df.mean()) / metrics_df.std()).fillna(0)
    df["Z_Score_Average"] = z_scores_df.mean(axis=1).round(2)

    plot_data = pd.concat([
        df[['Player', 'Team', 'Age', 'Height', 'Z_Score_Average']],
        metrics_df,
        percentile_df.add_suffix(' (percentile)')
    ], axis=1)

    # Metric groups and colors
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

    # Player selection
    players = plot_data['Player'].dropna().unique().tolist()
    selected_player = st.selectbox("Choose a player", players)

    if selected_player:
        selected_row = plot_data[plot_data['Player'] == selected_player]
        avg_z = selected_row["Z_Score_Average"].values[0]
        if avg_z >= 1:
            badge_color = "green"
            badge_text = "Excellent"
        elif avg_z >= 0.5:
            badge_color = "blue"
            badge_text = "Above Average"
        elif avg_z >= 0:
            badge_color = "orange"
            badge_text = "Average"
        else:
            badge_color = "red"
            badge_text = "Below Average"

        st.markdown(f"<h3 style='text-align: center;'>Average Z Score – {avg_z:.2f}</h3>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center;'><span style='background-color:{badge_color}; color:white; padding:6px 15px; border-radius:8px;'>{badge_text}</span></div>", unsafe_allow_html=True)

        plot_radial_bar_grouped(selected_player, plot_data, metric_groups, group_colors)

    # Player list ranked by Z Score
    st.subheader("Players Ranked by Z Score")
    sorted_df = df[['Player', 'Team', 'Z_Score_Average']].sort_values(by='Z_Score_Average', ascending=False).reset_index(drop=True)
    st.dataframe(sorted_df, use_container_width=True)
