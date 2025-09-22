import pandas as pd

match_data = pd.read_csv("data/match_data.csv")

match_data.drop(columns=["Unnamed: 0", "city", "method"], inplace=True)

final_match_data = match_data.dropna()

def normalize_match_type(x):

    # Finals
    if x in ["Final"]:
        return "Final"

    # First eliminator (Qualifier 1 / Eliminator / Semi Final)
    elif x in ["Qualifier 1", "Elimination Final", "Eliminator", "Semi Final"]:
        return "Eliminator 1"

    # Second eliminator (Qualifier 2 / 3rd place playoff, etc.)
    elif x in ["Qualifier 2", "3rd Place Play-Off"]:
        return "Eliminator 2"

    # Everything else (numbers 1–70)
    else:
        return "League"

# Apply on your dataframe
final_match_data.loc[:, "match_type"] = final_match_data["match_type"].apply(normalize_match_type)

########## Cleaning team names values z

def normalize_team(team):
    mapping = {
        # RCB
        "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
        "Royal Challengers Bengaluru": "Royal Challengers Bengaluru",

        # Punjab
        "Kings XI Punjab": "Punjab Kings",
        "Punjab Kings": "Punjab Kings",

        # Delhi
        "Delhi Daredevils": "Delhi Capitals",
        "Delhi Capitals": "Delhi Capitals",
        "�Delhi Capitals": "Delhi Capitals",   # fix encoding issue

        # Mumbai
        "Mumbai Indians": "Mumbai Indians",

        # KKR
        "Kolkata Knight Riders": "Kolkata Knight Riders",

        # Rajasthan
        "Rajasthan Royals": "Rajasthan Royals",

        # Deccan Chargers → now defunct, map to Sunrisers
        "Deccan Chargers": "Sunrisers Hyderabad",
        "Sunrisers Hyderabad": "Sunrisers Hyderabad",

        # Kochi Tuskers (defunct, ignore or map nowhere, safest is NaN)
        "Kochi Tuskers Kerala": None,

        # Pune Warriors (defunct, ignore)
        "Pune Warriors": None,

        # Rising Pune → defunct, ignore
        "Rising Pune Supergiants": None,
        "Rising Pune Supergiant": None,

        # Gujarat
        "Gujarat Lions": "Gujarat Titans",
        "Gujarat Titans": "Gujarat Titans",

        # Lucknow
        "Lucknow Super Giants": "Lucknow Super Giants",

        # Chennai
        "Chennai Super Kings": "Chennai Super Kings"
    }
    return mapping.get(team, None)   # None if not in current 10 teams

def calculate_rolling_stats(df):
    team_stats = {}
    venue_stats = {}        # {venue: {team: {"matches": int, "wins": int}}}
    h2h_stats = {}          # {(team1, team2): {"matches": int, "wins": int}}

    features = []

    for _, row in df.iterrows():
        t1, t2 = row["team1"], row["team2"]
        venue = row["venue"]

        # Initialize team stats
        for team in [t1, t2]:
            if team not in team_stats:
                team_stats[team] = {"matches": 0, "wins": 0, "streak": 0, "recent": []}

        # Initialize venue stats
        if venue not in venue_stats:
            venue_stats[venue] = {}
        for team in [t1, t2]:
            if team not in venue_stats[venue]:
                venue_stats[venue][team] = {"matches": 0, "wins": 0}

        # Initialize h2h stats
        for a, b in [(t1, t2), (t2, t1)]:
            if (a, b) not in h2h_stats:
                h2h_stats[(a, b)] = {"matches": 0, "wins": 0}

        # -------- GET FEATURES *BEFORE* MATCH -------- #
        def get_team_features(team_f):
            stats = team_stats[team_f]
            matches, wins, streak, recent = stats["matches"], stats["wins"], stats["streak"], stats["recent"]
            win_ratio = wins / matches if matches > 0 else 0.5
            recent_form = sum(recent[-5:]) / min(len(recent), 5) if recent else 0.5
            return win_ratio, recent_form, streak

        def get_venue_features(team):
            vstats = venue_stats[venue][team]
            return vstats["wins"] / vstats["matches"] if vstats["matches"] > 0 else 0.5

        def get_h2h_features(team_a, team_b):
            hstats = h2h_stats[(team_a, team_b)]
            return hstats["wins"] / hstats["matches"] if hstats["matches"] > 0 else 0.5

        # Team stats
        t1_wr, t1_form, t1_streak = get_team_features(t1)
        t2_wr, t2_form, t2_streak = get_team_features(t2)

        # Venue stats
        t1_venue_wr = get_venue_features(t1)
        t2_venue_wr = get_venue_features(t2)

        # H2H stats
        h2h_wr = get_h2h_features(t1, t2)

        # Save features BEFORE current match is updated
        features.append({
            "team1_win_ratio": t1_wr,
            "team2_win_ratio": t2_wr,
            "team1_recent_form": t1_form,
            "team2_recent_form": t2_form,
            "team1_streak": t1_streak,
            "team2_streak": t2_streak,
            "venue_team1_winrate": t1_venue_wr,
            "venue_team2_winrate": t2_venue_wr,
            "head_to_head_winrate": h2h_wr,
        })

        # -------- UPDATE AFTER MATCH (safe: only affects future matches) -------- #
        winner = row["winner"]

        for team in [t1, t2]:
            team_stats[team]["matches"] += 1
            if team == winner:
                team_stats[team]["wins"] += 1
                team_stats[team]["streak"] = max(1, team_stats[team]["streak"] + 1)
                team_stats[team]["recent"].append(1)
            else:
                team_stats[team]["streak"] = min(-1, team_stats[team]["streak"] - 1)
                team_stats[team]["recent"].append(0)

        for team in [t1, t2]:
            venue_stats[venue][team]["matches"] += 1
            if team == winner:
                venue_stats[venue][team]["wins"] += 1

        h2h_stats[(t1, t2)]["matches"] += 1
        h2h_stats[(t2, t1)]["matches"] += 1
        if winner == t1:
            h2h_stats[(t1, t2)]["wins"] += 1
        elif winner == t2:
            h2h_stats[(t2, t1)]["wins"] += 1

    # Merge rolling features into original dataframe
    feats_df = pd.DataFrame(features)
    df = df.reset_index(drop=True)
    df = pd.concat([df, feats_df], axis=1)

    return df


final_match_data.loc[:, "team1"] = final_match_data["team1"].apply(normalize_team)
final_match_data.loc[:, "team2"] = final_match_data["team2"].apply(normalize_team)
final_match_data.loc[:, "toss_winner"] = final_match_data["toss_winner"].apply(normalize_team)
final_match_data.loc[:, "winner"] = final_match_data["winner"].apply(normalize_team)

final_match_data.isna().sum()

l_clean_data = final_match_data.dropna()

########## cleaning str columns

l_clean_data = l_clean_data.copy()
l_clean_data["toss_decision"] = l_clean_data["toss_decision"].str.lower()

l_clean_data["result"] = l_clean_data["result"].str.lower()

############ cleaning date column

final_match_data_ipl = l_clean_data.drop(columns=["date"])


data = final_match_data_ipl.copy()

data.rename(columns={'id': 'match_id'}, inplace=True)

data.to_csv("match_data.csv")
