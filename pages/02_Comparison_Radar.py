# pages/02_Comparison_Radar.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from shared_templates import (
    SIX_GROUPS, RAW_TO_SIX, DEFAULT_TEMPLATE, position_metrics,
    map_first_position_to_group
)

PASSWORD = "cowboy"

st.title("⚔️ Player Comparison Radar")

# Password
pwd = st.text_input("Enter password:", type="password")
if pwd != PASSWORD:
    st.warning("Please enter the correct password to access the app.")
    st.stop()

# File upload
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"], key="comp_upload")
if not uploaded_file:
    st.stop()
df = pd.read_excel(uploaded_file)

# Positions played and six group
if "Position" in df.columns:
    df["Positions played"] = df["Position"].astype(str)
else:
    df["Positions played"] = np.nan
df["Six-Group Position"] = df["Position"].apply(map_first_position_to_group) if "Position" in df.columns else np.nan

# Minutes filter
minutes_col = "Minutes played"
min_minutes = st.number_input("Minimum minutes to include", min_value=0, value=1000, step=50, key="comp_min")
df["_minutes_numeric"] = pd.to_numeric(df.get(minutes_col, np.nan), errors="coerce")
df = df[df["_minutes_numeric"] >= min_minutes].copy()
if df.empty:
    st.warning("No players meet the minutes threshold.")
    st.stop()

# Age filter
if "Age" in df.columns:
    df["_age_numeric"] = pd.to_numeric(df["Age"], errors="coerce")
    if df["_age_numeric"].notna().any():
        a_min = int(np.nanmin(df["_age_numeric"]))
        a_max = int(np.nanmax(df["_age_numeric"]))
        sel_min, sel_max = st.slider("Age range to include", min_value=a_min, max_value=a_max, value=(a_min, a_max), step=1, key="comp_age")
        df = df[df["_age_numeric"].between(sel_min, sel_max)].copy()
st.caption(f"Filtering on '{minutes_col}' ≥ {min_minutes}. Players remaining, {len(df)}")

# 6-group filter
available_groups = [g for g in SIX_GROUPS if g in df["Six-Group Position"].unique()]
selected_groups = st.multiselect("Include groups", options=available_groups, default=[], label_visibility="collapsed", key="comp_groups")
if selected_groups:
    df = df[df["Six-Group Position"].isin(selected_groups)].copy()
    if df.empty:
        st.warning("No players after 6-group filter.")
        st.stop()

# Template selection
group_for_default = selected_groups[0] if selected_groups else df["Six-Group Position"].dropna().iloc[0] if not df.empty else None
default_template = DEFAULT_TEMPLATE.get(group_for_default, list(position_metrics.keys())[0])
template_names = list(position_metrics.keys())
selected_template = st.selectbox("Choose a position template for the chart", template_names, index=template_names.index(default_template) if default_template in template_names else 0, key="comp_template")

# Choose players, up to two
players_all = df["Player"].dropna().unique().tolist()
default_pick = players_all[:2] if len(players_all) >= 2 else players_all[:1]
selected_players = st.multiselect("Choose one or two players to compare", options=players_all, default=default_pick, max_selections=2, key="comp_players")

if len(selected_players) == 0:
    st.info("Pick at least one player")
    st.stop()

# Ensure template metrics exist
metrics = position_metrics[selected_template]["metrics"]
for m in metrics:
    if m not in df.columns:
        df[m] = 0.0
df[metrics] = df[metrics].apply(pd.to_numeric, errors="coerce").fillna(0.0)

# Percentiles for these metrics within current filtered df
metrics_df = df[metrics].copy()
percentile_df = (metrics_df.rank(pct=True) * 100).round(1)

keep_cols = ["Player", "Team", "Team within selected timeframe", "Age", "Minutes played"]
plot_data = pd.concat([df[keep_cols], metrics_df, percentile_df.add_suffix(" (percentile)")], axis=1)

def plot_comparison_radar(players_list, plot_data, metrics, template_title):
    import numpy as np
    import matplotlib.pyplot as plt

    colors = ["#1f77b4", "#ff7f0e"]  # blue, orange
    labels = [m.replace(" per 90", "").replace(", %", " (%)") for m in metrics]
    n = len(metrics)
    angles = np.linspace(0, 2*np.pi, n, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_theta_offset(np.pi/2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 100)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10, fontweight="bold")
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=9)
    ax.grid(True, alpha=0.3)

    for i, name in enumerate(players_list):
        color = colors[i % 2]
        row = plot_data.loc[plot_data["Player"] == name]
        if row.empty:
            continue
        vals = row[[m + " (percentile)" for m in metrics]].values.flatten().tolist()
        vals += vals[:1]
        ax.plot(angles, vals, linewidth=2.5, linestyle="-", marker="o", markersize=5, color=color, alpha=0.95)
        ax.fill(angles, vals, color=color, alpha=0.25, zorder=2)

    if len(players_list) == 2:
        title_html = f"<span style='color:{colors[0]};font-weight:800'>{players_list[0]}</span> vs " \
                     f"<span style='color:{colors[1]};font-weight:800'>{players_list[1]}</span>"
    else:
        title_html = f"<span style='color:{colors[0]};font-weight:800'>{players_list[0]}</span>"

    st.markdown(f"<div style='text-align:center;font-size:24px;margin:10px 0;'>{title_html}</div>", unsafe_allow_html=True)
    ax.set_title(template_title, va="bottom", fontsize=14, pad=20)
    if len(players_list) == 2:
        ax.legend(players_list, loc="upper right", bbox_to_anchor=(1.18, 1.12))
    st.pyplot(fig)

plot_comparison_radar(selected_players, plot_data, metrics, selected_template)

# Optional table with raw and percentile for chosen players
st.markdown("#### Values, raw and percentile")
cols = ["Player"] + metrics + [m + " (percentile)" for m in metrics]
st.dataframe(plot_data[plot_data["Player"].isin(selected_players)][cols].reset_index(drop=True), use_container_width=True)
