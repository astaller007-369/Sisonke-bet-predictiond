import os
import json
import math
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Sisonke Bet Predictions", page_icon="⚽", layout="wide")

# FIX: Changed unsafe_allow_path=True to unsafe_allow_html=True to prevent structural layout crashes
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #f1f5f9; }
    h1 { color: #facc15; font-weight: 900 !important; font-size: 42px !important; margin: 0; padding-bottom: 5px; }
    h3 { color: #facc15; font-weight: 700 !important; margin-top: 25px !important; border-bottom: 1px solid #1e293b; padding-bottom: 5px; }
    
    .metric-card { 
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #334155; 
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-title { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
    .metric-value { font-size: 28px; font-weight: 800; line-height: 1; margin: 0; }
    
    .market-header { 
        color: #38bdf8; 
        font-weight: 700; 
        font-size: 15px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        border-bottom: 2px solid #0284c7; 
        margin-top: 15px; 
        margin-bottom: 12px;
        padding-bottom: 4px; 
    }
    
    .live-badge {
        background-color: #ef4444;
        color: #ffffff;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        animation: blinker 1.5s linear infinite;
    }
    @keyframes blinker { 50% { opacity: 0.4; } }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=10)
def load_data():
    if os.path.exists("dashboard_data.json"):
        with open("dashboard_data.json", "r") as f:
            return json.load(f)
    return None

data = load_data()

st.write("<h1>Sis⚽nke Bet Predictions</h1>", unsafe_allow_html=True)
st.caption("Advanced Bivariate Poisson Forecasting Network & Live Analytics Suite")

if not data:
    st.error("Data tracking source not detected. Ensure background pipeline has populated dashboard_data.json.")
    st.stop()

m = data.get("metrics", {})
perf = data.get("performance_audit", {})
dl_audit = perf.get("domestic_league_suite", {"dynamic_brier_skill_score": 0.0})
it_audit = perf.get("international_tournament_suite", {"dynamic_brier_skill_score": 0.0})

m_cols = st.columns(5)
m_configs = [
    {"title": "Overall Win Rate", "val": f"{m.get('overall_win_pct', 0.0)}%", "color": "#10b981"},
    {"title": "28-Day Accuracy", "val": f"{m.get('accuracy_28_day', 0.0)}%", "color": "#eab308"},
    {"title": "Settled Ledger Count", "val": str(m.get("total_backtested", 0)), "color": "#38bdf8"},
    {"title": "Dynamic BSS (League)", "val": f"{dl_audit.get('dynamic_brier_skill_score', 0.0):.3f}", "color": "#a855f7"},
    {"title": "Dynamic BSS (Tourney)", "val": f"{it_audit.get('dynamic_brier_skill_score', 0.0):.3f}", "color": "#f43f5e"}
]

for idx, config in enumerate(m_configs):
    m_cols[idx].markdown(
        f'<div class="metric-card">'
        f'  <p class="metric-title" style="color:{config["color"]};">{config["title"]}</p>'
        f'  <p class="metric-value">{config["val"]}</p>'
        f'</div>', 
        unsafe_allow_html=True
    )

leagues_matrix = {
    "England Premier League & Cups": "england", "Spain La Liga & Cups": "spain",
    "France Ligue 1 & Cups": "france", "Germany Bundesliga & Cups": "germany",
    "Italy Serie A & Cups": "italy", "Iran Persian Gulf Pro League": "iran",
    "South Africa Premier Soccer League": "south_africa", "Morocco Botola Pro": "morocco",
    "Tunisia Ligue Professionnelle 1": "tunisia", "China Super League": "china",
    "Portugal Primeira Liga": "portugal", "Scotland Scottish Premiership": "scotland",
    "Greece Super League": "greek", "South Korea K League 1": "south_korea",
    "Iceland Best deild karla": "iceland", "Ireland Premier Division": "ireland",
    "Estonia Meistriliiga": "estonia", "Latvia Virsliga": "latvia",
    "Croatia Football League": "croatia", "Egypt Premier League": "egypt",
    "Netherlands Eredivisie": "netherlands", "Serbia SuperLiga": "serbia",
    "Russia Premier League": "russia", "Slovenia PrvaLiga": "slovenia",
    "Uruguay Primera División": "uruguay", "Turkey Süper Lig": "turkey",
    "Belgium Pro League": "belgium", "Austria Bundesliga": "austria",
    "Switzerland Super League": "switzerland", "Czech First League": "czech",
    "Denmark Superliga": "denmark", "Brazil Série A & Copa": "brazil"
}

tab_live, tab_predictions, tab_standings, tab_history = st.tabs([
    "🔴 LIVE IN-PLAY CENTRE", 
    "📅 FUTURE PROJECTIONS", 
    "🌍 LEAGUE TABLES", 
    "📜 ARCHIVE LEDGER"
])

with tab_live:
    live_games = data.get("live_games", [])
    if live_games:
        for lg in live_games:
            with st.container(border=True):
                st.markdown(
                    f"### <span class='live-badge'>LIVE</span> {lg.get('home_team', 'Home')} "
                    f"**{lg.get('current_score', '0-0')}** {lg.get('away_team', 'Away')} ({lg.get('minute', 0)}') — "
                    f"*{lg.get('league_name', '').upper()}*", 
                    unsafe_allow_html=True
                )
                
                lc1, lc2, lc3, lc4 = st.columns(4)
                lc1.metric("Match Possession", lg.get("possession", "50% / 50%"))
                lc2.metric("Shots on Target (H/A)", f"{lg.get('home_sot', 0)} - {lg.get('away_sot', 0)}")
                lc3.metric("Dangerous Attacks (H/A)", f"{lg.get('home_dangerous_attacks', 0)} / {lg.get('away_dangerous_attacks', 0)}")
                
                sh = lg.get("second_half_forecast", {}).get("sh_probabilities", {"HOME": 0.33, "DRAW": 0.34, "AWAY": 0.33})
                with lc4:
                    st.markdown("**Live 2H Forecast Model:**")
                    st.caption(f"🏠 H: **{sh.get('HOME', 0.33)*100:.1f}%** | 🤝 D: **{sh.get('DRAW', 0.34)*100:.1f}%** | 🚀 A: **{sh.get('AWAY', 0.33)*100:.1f}%**")
    else:
        st.info("No active live games currently running. In-play tickers populate instantly upon match kickoff.")

with tab_predictions:
    upcoming_raw = data.get("future_predictions", [])
    if upcoming_raw:
        upcoming_df = pd.DataFrame(upcoming_raw)
        upcoming_df["match_timestamp"] = pd.to_datetime(upcoming_df["match_timestamp"])
        upcoming_df = upcoming_df.sort_values(by="match_timestamp", ascending=True).reset_index(drop=True)
        
        st.markdown("### Chronological Multi-Market Predictions (Earliest Kickoffs First)")
        rows = []
        for idx, x in upcoming_df.iterrows():
            mkts = x.get("market_projections", {})
            p_1x2 = mkts.get("1X2", {"HOME": 0.33, "DRAW": 0.34, "AWAY": 0.33})
            p_ou25 = mkts.get("over_under_2.5", {"OVER": 0.5, "UNDER": 0.5})
            p_btts = mkts.get("btts", {"YES": 0.5, "NO": 0.5})
            
            flag_val = "-"
            if x.get("tournament_mode_active", False):
                flag_val = "✈️ TOURNEY MODE"
            elif len(x.get("value_bets_detected", [])) > 0:
                flag_val = "⚠️ VALUE BET"
                
            rows.append({
                "Kickoff": str(x["match_timestamp"])[:16],
                "League Group": str(x.get("league_key", "england")).upper(),
                "Fixture Matchup": f"{x.get('home_team', 'Home')} vs {x.get('away_team', 'Away')}",
                "Primary Pick": x.get("predicted_outcome_1x2", "DRAW"),
                "1X2 Split (H/D/A)": f"{p_1x2.get('HOME', 0.33)*100:.0f}% / {p_1x2.get('DRAW', 0.34)*100:.0f}% / {p_1x2.get('AWAY', 0.33)*100:.0f}%",
                "O/U 2.5 Goals Line": f"O: {p_ou25.get('OVER', 0.5)*100:.0f}% | U: {p_ou25.get('UNDER', 0.5)*100:.0f}%",
                "BTTS Projections": f"Y: {p_btts.get('YES', 0.5)*100:.0f}% | N: {p_btts.get('NO', 0.5)*100:.0f}%",
                "Variant Mode Tag": flag_val
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        
        st.markdown("### 🔍 Advanced Match Drill-Down Lab")
        options_map = {f"[{row.get('league_key', 'LN').upper()}] {row.get('home_team', 'Home')} vs {row.get('away_team', 'Away')} ({str(row.get('match_timestamp'))[:16]})": row for idx, row in upcoming_df.iterrows()}
        sel_match = st.selectbox("Select Target Profile to Extract Probabilities Density Matrices:", list(options_map.keys()))
        
        if sel_match:
            target = options_map[sel_match]
            mkts = target.get("market_projections", {})
            
            c_left, c_right = st.columns(2)
            
            with c_left:
                # FIX: Changed to unsafe_allow_html=True
                st.markdown('<div class="market-header">Poisson Curve Probability Matrix Density</div>', unsafe_allow_html=True)
                exp_g = target.get("expected_goals", {"home": 1.4, "away": 1.1})
                goals_axis = np.arange(0, 6)
                home_dist = [(np.exp(-exp_g.get("home", 1.4)) * (exp_g.get("home", 1.4)**k)) / math.factorial(k) for k in goals_axis]
                away_dist = [(np.exp(-exp_g.get("away", 1.1)) * (exp_g.get("away", 1.1)**k)) / math.factorial(k) for k in goals_axis]
                
                chart_df = pd.DataFrame({
                    "Goals": goals_axis,
                    f"Home ({target.get('home_team', 'Home')})": home_dist,
                    f"Away ({target.get('away_team', 'Away')})": away_dist
                }).set_index("Goals")
                st.bar_chart(chart_df, use_container_width=True)
                
            with c_right:
                # FIX: Changed to unsafe_allow_html=True
