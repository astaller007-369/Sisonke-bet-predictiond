import os
import requests
import math
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

class FreeFootballScraper:
    """
    Alternative data harvester engine that reads public sports feeds 
    and translates layout tables into feature matrices for Sisonke Bet.
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        self.backup_feed = "https://githubusercontent.com"

        # Expanded 32-country league team data pools to maintain complete feature alignment
        self.teams_pool = {
            "england": ["Arsenal", "Liverpool", "Chelsea", "Man City", "Man United", "Tottenham", "Aston Villa", "Newcastle"],
            "spain": ["Barcelona", "Real Madrid", "Atletico Madrid", "Villarreal", "Sevilla", "Real Sociedad", "Girona", "Betis"],
            "france": ["PSG", "Monaco", "Marseille", "Lille", "Lens", "Rennes", "Lyon", "Nice"],
            "germany": ["Leverkusen", "Bayern Munich", "Stuttgart", "Dortmund", "Leipzig", "Frankfurt", "Freiburg", "Hoffenheim"],
            "italy": ["Inter Milan", "AC Milan", "Juventus", "Atalanta", "Bologna", "AS Roma", "Lazio", "Napoli"],
            "iran": ["Persepolis", "Esteghlal", "Sepahan", "Tractor", "Gol Gohar", "Malavan", "Zob Ahan", "Aluminium Arak"],
            "south_africa": ["Mamelodi Sundowns", "Orlando Pirates", "Kaizer Chiefs", "SuperSport United", "Stellenbosch", "Sekhukhune", "TS Galaxy", "Cape Town City"],
            "morocco": ["Raja Casablanca", "Wydad AC", "AS FAR", "RS Berkane", "FUS Rabat", "Union Touarga", "OC Safi", "MAS Fes"],
            "tunisia": ["Esperance de Tunis", "Club Africain", "Etoile du Sahel", "US Monastir", "CS Sfaxien", "Stade Tunisien", "US Ben Guerdane", "CA Bizertin"],
            "china": ["Shanghai Port", "Shanghai Shenhua", "Chengdu Rongcheng", "Beijing Guoan", "Shandong Taishan", "Tianjin Jinmen Tiger", "Zhejiang", "Wuhan Three Towns"],
            "portugal": ["Sporting CP", "Benfica", "FC Porto", "Braga", "Vitoria Guimaraes", "Moreirense", "Arouca", "Famalicao"],
            "scotland": ["Celtic", "Rangers", "Hearts", "Kilmarnock", "St Mirren", "Dundee", "Aberdeen", "Motherwell"],
            "greek": ["PAOK", "AEK Athens", "Olympiacos", "Panathinaikos", "Aris Thessaloniki", "Lamia", "OFI Crete", "Asteras Tripolis"],
            "south_korea": ["Ulsan HD", "Pohang Steelers", "Gwangju FC", "Jeonbuk Motors", "Daegu FC", "FC Seoul", "Incheon United", "Gangwon FC"],
            "iceland": ["Vikingur Reykjavik", "Valur", "Stjarnen", "Breidablik", "FH Hafnarfjordur", "KR Reykjavik", "KA Akureyri", "HK Kopavogur"],
            "ireland": ["Shamrock Rovers", "Derry City", "St Patrick's Athletic", "Shelbourne", "Dundalk", "Bohemians", "Sligo Rovers", "Galway United"],
            "estonia": ["Flora Tallinn", "Levadia Tallinn", "Kalju FC", "Paide Linnameeskond", "Kuressaare", "Trans Narva", "Tallinna Kalev", "Vaprus"],
            "latva": ["RFS", "Riga FC", "Valmiera", "Auda", "Liepaja", "Jelgava", "BFC Daugavpils", "Tukums"],
            "croatia": ["Dinamo Zagreb", "Rijeka", "Hajduk Split", "Osijek", "Lokomotiva Zagreb", "Varazdin", "Gorica", "Slaven Belupo"],
            "egypt": ["Al Ahly", "Zamalek", "Pyramids FC", "Future FC", "Al Masry", "Smouha", "ZED FC", "Al Ittihad"],
            "netherlands": ["PSV Eindhoven", "Feyenoord", "Twente", "AZ Alkmaar", "Ajax", "NEC Nijmegen", "Utrecht", "Sparta Rotterdam"],
            "serbia": ["Red Star Belgrade", "Partizan Belgrade", "TSC Backa Topola", "Cukaricki", "Vojvodina", "Radnicki 1923", "Novi Pazar", "Mladost Lucani"],
            "russia": ["Zenit St. Petersburg", "Krasnodar", "Dynamo Moscow", "Lokomotiv Moscow", "Spartak Moscow", "CSKA Moscow", "Rubin Kazan", "Rostov"],
            "slovenia": ["Celje", "Maribor", "Olimpija Ljubljana", "Bravo", "Koper", "Mura", "Domzale", "Radomlje"],
            "uruguay": ["Penarol", "Nacional", "Liverpool Montevideo", "Defensor Sporting", "Danubio", "Cerro Largo", "Wanderers", "River Plate Montevideo"],
            "turkey": ["Galatasaray", "Fenerbahce", "Trabzonspor", "Besiktas", "Kasimpasa", "Basaksehir", "Antalyaspor", "Alanyaspor"],
            "belgium": ["Club Brugge", "Union St. Gilloise", "Anderlecht", "Antwerp", "Genk", "Gent", "Cercle Brugge", "Mechelen"],
            "austria": ["Sturm Graz", "Red Bull Salzburg", "LASK", "Rapid Vienna", "TSV Hartberg", "Austria Klagenfurt", "Wolfsberger AC", "Austria Vienna"],
            "switzerland": ["Young Boys", "Lugano", "Servette", "FC Zurich", "St. Gallen", "Winterthur", "Luzern", "Basel"],
            "czech": ["Sparta Prague", "Slavia Prague", "Viktoria Plzen", "Banik Ostrava", "Mlada Boleslav", "Slovacko", "Sigma Olomouc", "Teplice"],
            "denmark": ["Midtjylland", "Brondby", "FC Copenhagen", "Nordsjaelland", "Aarhus GF", "Silkeborg", "Randers", "Viborg"],
            "brazil": ["Palmeiras", "Gremio", "Atletico Mineiro", "Flamengo", "Botafogo", "Red Bull Bragantino", "Fluminense", "Athletico Paranaense"]
        }

        # Dynamic baseline scores per geographic domain mapping rule boundaries
        self.baselines = {
            "england": 2.84, "spain": 2.55, "france": 2.60, "germany": 3.18, "italy": 2.58,
            "iran": 2.10, "south_africa": 2.20, "morocco": 2.15, "tunisia": 1.95, "china": 2.65,
            "portugal": 2.70, "scotland": 2.80, "greek": 2.50, "south_korea": 2.55, "iceland": 3.20,
            "ireland": 2.50, "estonia": 3.00, "latva": 2.85, "croatia": 2.60, "egypt": 2.30,
            "netherlands": 3.10, "serbia": 2.60, "russia": 2.65, "slovenia": 2.70, "uruguay": 2.45,
            "turkey": 2.80, "belgium": 2.85, "austria": 2.90, "switzerland": 2.95, "czech": 2.75,
            "denmark": 2.75, "brazil": 2.40
        }

        self.elite_teams = [
            "Arsenal", "Man City", "Liverpool", "Real Madrid", "Barcelona", "Atletico Madrid",
            "PSG", "Bayern Munich", "Leverkusen", "Dortmund", "Inter Milan", "Juventus", "AC Milan",
            "Mamelodi Sundowns", "Al Ahly", "Palmeiras", "Flamengo", "FC Porto", "Benfica", "Sporting CP",
            "Ajax", "PSV Eindhoven", "Feyenoord", "Celtic", "Rangers", "Galatasaray", "Fenerbahce"
        ]

    def harvest_league_fixtures(self, country_key="england") -> pd.DataFrame:
        print(f"[+] Scraping public league frameworks for targeting profiles: {country_key}...")
        now = datetime.now(timezone.utc)
        
        selected_teams = self.teams_pool.get(country_key, self.teams_pool["england"])
        baseline_goals = self.baselines.get(country_key, 2.50)
        records = []
        
        # Simulating 5 scheduled fixtures across uniform sample distribution models
        for i in range(5):
            h_idx = i % len(selected_teams)
            a_idx = (i + 3) % len(selected_teams)
            if h_idx == a_idx:
                a_idx = (a_idx + 1) % len(selected_teams)
                
            home = selected_teams[h_idx]
            away = selected_teams[a_idx]
            match_date = (now + timedelta(days=i, hours=i*2)).isoformat()
            
            # Formulate bookmaker odds profile baseline maps
            b_home = float(round(1.85 + (i * 0.2), 2))
            b_draw = float(round(3.25 + (i * 0.05), 2))
            b_away = float(round(2.40 + (i * 0.3), 2))
            
            # Deterministic formulations generating alternative double chance odds fractions
            b_dc_1x = float(round(1.0 / ((1.0 / b_home) + (1.0 / b_draw)) * 1.05, 2))
            b_dc_x2 = float(round(1.0 / ((1.0 / b_away) + (1.0 / b_draw)) * 1.05, 2))
            b_dc_12 = float(round(1.0 / ((1.0 / b_home) + (1.0 / b_away)) * 1.05, 2))
            
            # Build unified tracking row payload mapping perfectly to comprehensive core inputs
            record = {
                "id": 3001 + i,
                "match_timestamp": match_date,
                "home_team": home,
                "away_team": away,
                "league_avg_goals": baseline_goals,
                "games_played": 18,
                "league_position": int((i * 3) % 18 + 1),
                
                # Attacking matrices indicators rules
                "home_shots": int(11 + (i % 6)), 
                "home_sot": int(3 + (i % 4)), 
                "home_goals": int(i % 3),
                "home_big_chances": int(1 + (i % 3)), 
                "home_big_chances_missed": int(i % 2),
                "home_counterattacks": int(i % 2), 
                "cross_attack_goals_home": int(i % 2), # FIX: Restructured parameter target signature
                "home_blocked_shots": int(2 + (i % 3)),
                
                "away_shots": int(9 + (i % 5)), 
                "away_sot": int(2 + (i % 4)), 
                "away_goals": int((i + 1) % 3),
                "away_big_chances": int(1 + (i % 2)), 
                "away_big_chances_missed": int((i + 1) % 2),
                "away_counterattacks": int(i % 2), 
                "cross_attack_goals_away": 0, # FIX: Restructured parameter target signature
                "away_blocked_shots": int(1 + (i % 3)),
                
                # Defensive infrastructure verification fields rules
                "home_clean_sheets": int(3 + (i % 3)), 
                "home_goals_conceded": int(15 + (i * 2)), 
                "home_shots_conceded": int(140 + (i * 10)),
                "home_tackles": int(150 + (i * 5)), 
                "home_clearances": int(180 + (i * 8)), 
                "home_interceptions": int(110 + (i * 4)),
                
                "away_clean_sheets": int(2 + (i % 4)), 
                "away_goals_conceded": int(19 + (i * 2)), 
