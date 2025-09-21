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
