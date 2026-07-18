import os
import sys
import json
import math
import numpy as np
import pandas as pd

# Updated matrix mapping with tier 2 baseline goals isolated strictly to the top 5 European leagues
COMPETITION_MATRIX = {
    "england": {
        "tier_1": "Premier League", "baseline_goals": 2.84,
        "tier_2": "Championship", "tier_2_baseline_goals": 2.68,
        "cups": ["FA Cup", "EFL Cup"]
    },
    "spain": {
        "tier_1": "La Liga", "baseline_goals": 2.55,
        "tier_2": "Segunda División", "tier_2_baseline_goals": 2.42,
        "cups": ["Copa del Rey", "Supercopa de España"]
    },
    "france": {
        "tier_1": "Ligue 1", "baseline_goals": 2.60,
        "tier_2": "Ligue 2", "tier_2_baseline_goals": 2.38,
        "cups": ["Coupe de France", "Trophée des Champions"]
    },
    "germany": {
        "tier_1": "Bundesliga", "baseline_goals": 3.18,
        "tier_2": "2. Bundesliga", "tier_2_baseline_goals": 3.02,
        "cups": ["DFB-Pokal", "DFL-Supercup"]
    },
    "italy": {
        "tier_1": "Serie A", "baseline_goals": 2.58,
        "tier_2": "Serie B", "tier_2_baseline_goals": 2.46,
        "cups": ["Coppa Italia", "Supercoppa Italiana"]
    },
    "iran": {"tier_1": "Persian Gulf Pro League", "baseline_goals": 2.10, "cups": ["Hazfi Cup"]},
    "south_africa": {"tier_1": "Premier Soccer League", "baseline_goals": 2.20, "cups": ["Nedbank Cup", "Carling Knockout Cup", "MTN 8"]},
    "morocco": {"tier_1": "Botola Pro", "baseline_goals": 2.15, "cups": ["Moroccan Throne Cup"]},
    "tunisia": {"tier_1": "Tunisian Ligue Professionnelle 1", "baseline_goals": 1.95, "cups": ["Tunisian Cup"]},
    "china": {"tier_1": "Chinese Super League", "baseline_goals": 2.65, "cups": ["Chinese FA Cup", "Chinese FA Super Cup"]},
    "portugal": {"tier_1": "Primeira Liga", "baseline_goals": 2.70, "cups": ["Taça de Portugal", "Taça da Liga"]},
    "scotland": {"tier_1": "Scottish Premiership", "baseline_goals": 2.80, "cups": ["Scottish Cup", "Scottish League Cup"]},
    "greek": {"tier_1": "Super League Greece", "baseline_goals": 2.50, "cups": ["Greek Football Cup"]},
    "south_korea": {"tier_1": "K League 1", "baseline_goals": 2.55, "cups": ["Korean FA Cup"]},
    "iceland": {"tier_1": "Best deild karla", "baseline_goals": 3.20, "cups": ["Icelandic Cup", "Icelandic League Cup"]},
    "ireland": {"tier_1": "League of Ireland Premier Division", "baseline_goals": 2.50, "cups": ["FAI Cup", "President's Cup"]},
    "estonia": {"tier_1": "Meistriliiga", "baseline_goals": 3.00, "cups": ["Estonian Cup"]},
    "latvia": {"tier_1": "Virsliga", "baseline_goals": 2.85, "cups": ["Latvian Cup"]},
    "croatia": {"tier_1": "Croatian Football League", "baseline_goals": 2.60, "cups": ["Croatian Football Cup"]},
    "egypt": {"tier_1": "Egyptian Premier League", "baseline_goals": 2.30, "cups": ["Egypt Cup", "Egyptian Super Cup"]},
    "netherlands": {"tier_1": "Eredivisie", "baseline_goals": 3.10, "cups": ["KNVB Cup", "Johan Cruyff Shield"]},
    "serbia": {"tier_1": "Serbian SuperLiga", "baseline_goals": 2.60, "cups": ["Serbian Cup"]},
    "russia": {"tier_1": "Russian Premier League", "baseline_goals": 2.65, "cups": ["Russian Cup", "Russian Super Cup"]},
    "slovenia": {"tier_1": "Slovenian PrvaLiga", "baseline_goals": 2.70, "cups": ["Slovenian Cup"]},
    "uruguay": {"tier_1": "Uruguayan Primera División", "baseline_goals": 2.45, "cups": ["Copa Uruguay"]},
    "turkey": {"tier_1": "Süper Lig", "baseline_goals": 2.80, "cups": ["Turkish Cup", "Turkish Super Cup"]},
    "belgium": {"tier_1": "Belgian Pro League", "baseline_goals": 2.85, "cups": ["Belgian Cup", "Belgian Super Cup"]},
    "austria": {"tier_1": "Austrian Football Bundesliga", "baseline_goals": 2.90, "cups": ["Austrian Cup"]},
    "switzerland": {"tier_1": "Swiss Super League", "baseline_goals": 2.95, "cups": ["Swiss Cup"]},
    "czech": {"tier_1": "Czech First League", "baseline_goals": 2.75, "cups": ["Czech Cup"]},
    "denmark": {"tier_1": "Danish Superliga", "baseline_goals": 2.75, "cups": ["Danish Cup"]},
    "brazil": {"tier_1": "Campeonato Brasileiro Série A", "baseline_goals": 2.40, "cups": ["Copa do Brasil"]}
}

def calculate_time_decay_weight(days_ago, half_life_days=45):
    return math.exp(-0.69314718056 * (days_ago / half_life_days))

def parse_live_team_data(historical_matches, target_team, current_timestamp, half_life_days=45):
    if len(historical_matches) == 0:
        return {
            "goals": 1.2, "goals_conceded": 1.2, "shots": 12.0, "sot": 4.5, "blocked_shots": 3.0,
            "big_chances": 1.5, "big_chances_missed": 1.0, "counterattacks": 0.8, "cross_attack_goals": 0.3,
            "clean_sheets": 0.25, "tackles": 15.0, "clearances": 18.0, "interceptions": 9.0, 
            "shots_conceded": 12.0, "games_played": 1.0, "recent_form_points": 1.5
        }

    total_weight = 0.0
    weighted_goals, weighted_conceded = 0.0, 0.0
    weighted_shots, weighted_sot, weighted_blocked = 0.0, 0.0, 0.0
    weighted_bc, weighted_bcm = 0.0, 0.0
    weighted_counter, weighted_cross_goals = 0.0, 0.0
    weighted_cs = 0.0
    weighted_tackles, weighted_clearances, weighted_interceptions = 0.0, 0.0, 0.0
    weighted_shots_conceded = 0.0
    
    target_ts = pd.to_datetime(current_timestamp)
    points_accumulator = 0.0
    matches_counted = 0
    
    sorted_matches = historical_matches.copy()
    sorted_matches["match_timestamp"] = pd.to_datetime(sorted_matches["match_timestamp"])
    sorted_matches = sorted_matches.sort_values(by="match_timestamp", ascending=False)
    
    for idx, match in sorted_matches.iterrows():
        match_ts = match["match_timestamp"]
        if match_ts >= target_ts:
            continue
            
        days_ago = max(0, (target_ts - match_ts).days)
        weight = calculate_time_decay_weight(days_ago, half_life_days)
        
        is_home = match["home_team"] == target_team
        role_prefix = "home_" if is_home else "away_"
        opp_prefix = "away_" if is_home else "home_"
        
        weighted_goals += match[f"{role_prefix}goals"] * weight
        weighted_shots += match[f"{role_prefix}shots"] * weight
        weighted_sot += match[f"{role_prefix}sot"] * weight
        weighted_blocked += match[f"{role_prefix}blocked_shots"] * weight
        weighted_bc += match[f"{role_prefix}big_chances"] * weight
        weighted_bcm += match[f"{role_prefix}big_chances_missed"] * weight
        weighted_counter += match[f"{role_prefix}counterattacks"] * weight
        weighted_cross_goals += match[f"{role_prefix}cross_attack_goals"] * weight
        
        g_conceded = match[f"{opp_prefix}goals"]
        weighted_conceded += g_conceded * weight
        weighted_cs += (1.0 if g_conceded == 0 else 0.0) * weight
        weighted_tackles += match[f"{role_prefix}tackles"] * weight
        weighted_clearances += match[f"{role_prefix}clearances"] * weight
        weighted_interceptions += match[f"{role_prefix}interceptions"] * weight
        weighted_shots_conceded += match[f"{opp_prefix}shots"] * weight
        
        if matches_counted < 5:
            if match[f"{role_prefix}goals"] > match[f"{opp_prefix}goals"]:
                points_accumulator += 3.0
            elif match[f"{role_prefix}goals"] == match[f"{opp_prefix}goals"]:
                points_accumulator += 1.0
            matches_counted += 1
            
        total_weight += weight

    div = max(0.01, total_weight)
    return {
        "goals": weighted_goals / div, "goals_conceded": weighted_conceded / div,
        "shots": weighted_shots / div, "sot": weighted_sot / div, "blocked_shots": weighted_blocked / div,
        "big_chances": weighted_bc / div, "big_chances_missed": weighted_bcm / div,
        "counterattacks": weighted_counter / div, "cross_attack_goals": weighted_cross_goals / div,
        "clean_sheets": weighted_cs / div, "tackles": weighted_tackles / div,
        "clearances": weighted_clearances / div, "interceptions": weighted_interceptions / div,
        "shots_conceded": weighted_shots_conceded / div, "games_played": float(div),
        "recent_form_points": points_accumulator / max(1, matches_counted)
    }

def calc_dynamic_big_mult(recent_form, league_pos, is_big):
    if is_big == 1:
        return 1.15 if (recent_form > 2.2 and league_pos <= 4) else 1.02
    return 0.95 if (recent_form < 1.2 and league_pos >= 15) else 1.00

def calc_expanded_att_strength_proxy(shots, sot, goals, big_chances, bc_missed, counter_attacks, cross_goals, blocked_shots, lg_avg_shots, lg_avg_xg):
    bc_total = big_chances + bc_missed
    proxy_xg = (bc_total * 0.60) + (counter_attacks * 0.25) + (cross_goals * 0.20) + (sot * 0.05)
    
    base_vol = ((shots / max(1, lg_avg_shots)) * 0.3) + ((sot / max(1, lg_avg_shots * 0.4)) * 0.4) + ((goals / max(1, lg_avg_xg)) * 0.3)
    high_value_creation = (bc_total / 2.0) * 0.4 + (counter_attacks / 1.5) * 0.3 + (cross_goals / 0.5) * 0.3
    
    finishing_efficiency = max(0.05, (goals / max(0.1, proxy_xg)))
    efficiency_penalty = finishing_efficiency * ((1.0 - (min(1.0, bc_missed / max(1, bc_total)) * 0.15)) if bc_total > 0 else 1.0)
    
    pressure_volume = (blocked_shots / 4.0)
    raw_att = (base_vol * 0.45) + (high_value_creation * 0.30) + (pressure_volume * 0.10) + (finishing_efficiency * 0.15)
    
    return raw_att, efficiency_penalty, proxy_xg

def calc_expanded_def_quality_proxy(cs, gc, shots_conceded, tackles, clearances, interceptions, lg_avg_cs, lg_avg_gc, lg_avg_shots_con, games):
    if games <= 0:
        return 1.0, 0.0
        
    cs_rate, gc_rate, sc_rate = cs / games, gc / games, shots_conceded / games
    tackle_rate, clear_rate, inter_rate = tackles / games, clearances / games, interceptions / games
    
    proxy_xga = (shots_conceded * 0.08) + (gc_rate * 0.4)
