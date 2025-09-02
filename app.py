import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

# --- Basic password protection ---
PASSWORD = "cowboy"

st.title("⚽ Radar Chart Explorer")

# Ask for password
pwd = st.text_input("Enter password:", type="password")
if pwd != PASSWORD:
    st.warning("Please enter the correct password to access the app.")
    st.stop()

# ========== 6-position mapping ==========
SIX_GROUPS = [
    "Goalkeeper",
    "Wide Defender",
    "Central Defender",
    "Central Midfielder",
    "Wide Midfielder",
    "Central Forward"
]

RAW_TO_SIX = {
    # Goalkeeper
    "GK": "Goalkeeper", "GKP": "Goalkeeper", "GOALKEEPER": "Goalkeeper",

    # Wide Defender
    "RB": "Wide Defender", "LB": "Wide Defender",
    "RWB": "Wide Defender", "LWB": "Wide Defender", "RFB": "Wide Defender", "LFB": "Wide Defender",

    # Central Defender
    "CB": "Central Defender", "RCB": "Central Defender", "LCB": "Central Defender",
    "CBR": "Central Defender", "CBL": "Central Defender", "SW": "Central Defender",

    # Central Midfielder
    "CMF": "Central Midfielder", "CM": "Central Midfielder",
    "RCMF": "Central Midfielder", "RCM": "Central Midfielder",
    "LCMF": "Central Midfielder", "LCM": "Central Midfielder",
    "DMF": "Central Midfielder", "DM": "Central Midfielder", "CDM": "Central Midfielder",
    "RDMF": "Central Midfielder", "RDM": "Central Midfielder",
    "LDMF": "Central Midfielder", "LDM": "Central Midfielder",
    "AMF": "Central Midfielder", "AM": "Central Midfielder", "CAM": "Central Midfielder",
    "SS": "Central Midfielder", "10": "Central Midfielder",

    # Wide Midfielder
    "LWF": "Wide Midfielder", "RWF": "Wide Midfielder",
    "RW": "Wide Midfielder", "LW": "Wide Midfielder",
    "LAMF": "Wide Midfielder", "RAMF": "Wide Midfielder",
    "RM": "Wide Midfielder", "LM": "Wide Midfielder",
    "WF": "Wide Midfielder", "RWG": "Wide Midfielder", "LWG": "Wide Midfielder", "W": "Wide Midfielder",

    # Central Forward
    "CF": "Central Forward", "ST": "Central Forward", "9": "Central Forward",
    "FW": "Central Forward", "STK": "Central Forward", "CFW": "Central Forward"
}

def _clean_pos_token(tok: str) -> str:
    if pd.isna(tok):
        return ""
    t = str(tok).upper()
    t = t.replace(".", "").replace("-", "").replace(" ", "")
    return t

def parse_first_position(cell) -> str:
    if pd.isna(cell):
        return ""
    first = re.split(r"[,/]", str(cell))[0].strip()
    return _clean_pos_token(first)

def map_first_position_to_group(cell) -> str:
    tok = parse_first_position(cell)
    return RAW_TO_SIX.get(tok, "Wide Midfielder")  # safe default

# ========== Metric sets ==========
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
            # Defensive
            "Successful defensive actions per 90", "Defensive duels per 90",
            "Defensive duels won, %", "PAdj Interceptions",
            # Possession
            "Crosses per 90", "Accurate crosses, %", "Dribbles per 90",
            "Successful dribbles, %", "Offensive duels per 90",
            "Offensive duels won, %", "Passes to final third per 90",
            "Accurate passes to final third, %",
            # Attacking
            "xA per 90", "Assists per 90"
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
            "Accurate passes to final third, %": "Possession",
            "xA per 90": "Attacking",
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
        "metrics": [
            "Defensive duels per 90", "Defensive duels won, %", "Aerial duels per 90",
            "Aerial duels won, %", "Shots blocked per 90", "PAdj Interceptions",
            "Head goals per 90", "Successful dribbles, %", "Accurate passes, %"
        ],
        "groups": {
            "Defensive duels per 90": "Defensive",
            "Defensive duels won, %": "Defensive",
            "Aerial duels per 90": "Defensive",
            "Aerial duels won, %": "Defensive",
            "Shots blocked per 90": "Defensive",
            "PAdj Interceptions": "Defensive",
            "Head goals per 90": "Possession",
            "Successful dribbles, %": "Possession",
            "Accurate passes, %": "Possession"
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

group_colors = {
    "Off The Ball": "crimson",
    "Attacking": "royalblue",
    "Possession": "seagreen",
    "Defensive": "darkorange"
}

# ---------- File upload ----------
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if not uploaded_file:
    st.stop()

df = pd.read_excel(uploaded_file)

# ---------- Positions ----------
if "Position" in df.columns:
    df["Positions played"] = df["Position"].astype(str)
else:
    df["Positions played"] = np.nan

# Derive your 6-group bucket from the FIRST listed position
df["Six-Group Position"] = df["Position"].apply(map_first_position_to_group) if "Position" in df.columns else np.nan

# ---------- Minutes filter ----------
minutes_col = "Minutes played"
min_minutes = st.number_input("Minimum minutes to include", min_value=0, value=1000, step=50)
df["_minutes_numeric"] = pd.to_numeric(df.get(minutes_col, np.nan), errors="coerce")
df = df[df["_minutes_numeric"] >= min_minutes].copy()
if df.empty:
    st.warning("No players meet the minutes threshold. Lower the minimum.")
    st.stop()

# ---------- Age slider filter ----------
if "Age" in df.columns:
    df["_age_numeric"] = pd.to_numeric(df["Age"], errors="coerce")
    if df["_age_numeric"].notna().any():
        age_min = int(np.nanmin(df["_age_numeric"]))
        age_max = int(np.nanmax(df["_age_numeric"]))
        sel_min, sel_max = st.slider(
            "Age range to include",
            min_value=age_min,
            max_value=age_max,
            value=(age_min, age_max),
            step=1
        )
        df = df[df["_age_numeric"].between(sel_min, sel_max)].copy()
    else:
        st.info("Age column has no numeric values, age filter skipped.")
else:
    st.info("No Age column found, age filter skipped.")

st.caption(f"Filtering on '{minutes_col}' ≥ {min_minutes}. Players remaining, {len(df)}")

# ---------- 6-group filter with no visible title ----------
available_groups = [g for g in SIX_GROUPS if g in df["Six-Group Position"].unique()]
selected_groups = st.multiselect(
    "Include groups",
    options=available_groups,
    default=[],
    label_visibility="collapsed"
)
if selected_groups:
    df = df[df["Six-Group Position"].isin(selected_groups)].copy()
    if df.empty:
        st.warning("No players after 6-group filter. Clear filters or choose different groups.")
        st.stop()

# ---------- Choose template for metrics ----------
selected_position_template = st.selectbox("Choose a position template for the chart", list(position_metrics.keys()))
metrics = position_metrics[selected_position_template]["metrics"]
metric_groups = position_metrics[selected_position_template]["groups"]

# Ensure metric columns exist
for m in metrics:
    if m not in df.columns:
        df[m] = 0
df[metrics] = df[metrics].fillna(0)

# Percentiles within filtered set
metrics_df = df[metrics].copy()
percentile_df = (metrics_df.rank(pct=True) * 100).round(1)

# Data for plotting and table
keep_cols = ["Player", "Team within selected timeframe", "Team", "Age", "Height", "Positions played", "Minutes played"]
plot_data = pd.concat([df[keep_cols], metrics_df, percentile_df.add_suffix(" (percentile)")], axis=1)

# --- Add Avg Z and Rank before the player select ---
sel_metrics = list(metric_groups.keys())
percentiles_all = plot_data[[m + " (percentile)" for m in sel_metrics]]
z_scores_all = (percentiles_all - 50) / 15
plot_data["Avg Z Score"] = z_scores_all.mean(axis=1)
plot_data["Rank"] = plot_data["Avg Z Score"].rank(ascending=False, method="min").astype(int)

# ---------- Player select and chart ----------
players = plot_data["Player"].dropna().unique().tolist()
selected_player = st.selectbox("Choose a player", players)

def plot_radial_bar_grouped(player_name, plot_data, metric_groups, group_colors):
    row = plot_data[plot_data["Player"] == player_name]
    if row.empty:
        st.error(f"No player named '{player_name}' found.")
        return

    sel_metrics_loc = list(metric_groups.keys())
    raw = row[sel_metrics_loc].values.flatten()
    percentiles = row[[m + " (percentile)" for m in sel_metrics_loc]].values.flatten()
    groups = [metric_groups[m] for m in sel_metrics_loc]
    colors = [group_colors[g] for g in groups]

    num_bars = len(sel_metrics_loc)
    angles = np.linspace(0, 2*np.pi, num_bars, endpoint=False)

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_theta_offset(np.pi/2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 100)
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.spines["polar"].set_visible(False)

    ax.bar(angles, percentiles, width=2*np.pi/num_bars*0.9, color=colors, edgecolor=colors, alpha=0.75)

    for angle, raw_val in zip(angles, raw):
        ax.text(angle, 50, f"{raw_val:.2f}", ha="center", va="center",
                color="black", fontsize=10, fontweight="bold", rotation=0)

    for i, angle in enumerate(angles):
        label = sel_metrics_loc[i].replace(" per 90", "").replace(", %", " (%)")
        ax.text(angle, 108, label, ha="center", va="center", rotation=0,
                color="black", fontsize=10, fontweight="bold")

    # Group labels
    group_positions = {}
    for g, a in zip(groups, angles):
        group_positions.setdefault(g, []).append(a)
    for group, group_angles in group_positions.items():
        mean_angle = np.mean(group_angles)
        ax.text(mean_angle, 125, group, ha="center", va="center",
                fontsize=20, fontweight="bold", color=group_colors[group], rotation=0)

    # Title lines, include minutes and rank
    age = row["Age"].values[0]
    height = row["Height"].values[0]
    team = row["Team within selected timeframe"].values[0]
    mins = row["Minutes played"].values[0] if "Minutes played" in row else np.nan
    rank_val = int(row["Rank"].values[0]) if "Rank" in row else None

    age_str = f"{int(age)} years old" if not pd.isnull(age) else ""
    height_str = f"{int(height)} cm" if not pd.isnull(height) else ""
    parts = [player_name]
    if age_str: parts.append(age_str)
    if height_str: parts.append(height_str)
    line1 = " | ".join(parts)

    team_str = f"{team}" if pd.notnull(team) else ""
    mins_str = f"{int(mins)} mins" if pd.notnull(mins) else ""
    rank_str = f"Rank #{rank_val}" if rank_val is not None else ""
    line2_parts = [team_str, mins_str, rank_str]
    line2 = " | ".join([p for p in line2_parts if p])

    ax.set_title(f"{line1}\n{line2}", color="black", size=22, pad=20, y=1.12)

    # Badge based on avg z of this player
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
        f"{badge[0]}</span></div>",
        unsafe_allow_html=True
    )

    st.pyplot(fig)

if selected_player:
    plot_radial_bar_grouped(selected_player, plot_data, metric_groups, group_colors)

# ---------- Ranking table ----------
st.markdown("### Players Ranked by Z-Score")
cols_for_table = [
    "Player", "Positions played", "Age", "Team", "Team within selected timeframe", "Minutes played", "Avg Z Score", "Rank"
]
z_ranking = (plot_data[cols_for_table]
             .sort_values(by="Avg Z Score", ascending=False)
             .reset_index(drop=True))

z_ranking[["Team", "Team within selected timeframe"]] = (
    z_ranking[["Team", "Team within selected timeframe"]].fillna("N/A")
)
if "Age" in z_ranking:
    z_ranking["Age"] = z_ranking["Age"].apply(lambda x: int(x) if pd.notnull(x) else x)

z_ranking.index = np.arange(1, len(z_ranking) + 1)
z_ranking.index.name = "Row"

st.dataframe(z_ranking, use_container_width=True)
