import pandas as pd
import joblib

# # Load encoders back
# encoders = joblib.load("label_encoders.pkl")
# match_data = pd.read_csv("match_data.csv")
# score_data = pd.read_csv("data/.csv")

# score_data.drop(columns=['Unnamed: 0'], inplace=True)

# score_data["team1"] = pd.Series(encoders["team"].transform(score_data["team1"]), index=score_data.index)
# score_data["team2"] = pd.Series(encoders["team"].transform(score_data["team2"]), index=score_data.index)

def merge_match_balls(match_data, score_data):
   
    # Drop team columns from score_data (already in match_data)
    score_data_clean = score_data.drop(columns=['team1','team2'], errors='ignore')

    # Merge on match_id, keep all matches from match_data
    merged_df = match_data.merge(score_data_clean, on='match_id', how='left', sort=False)

    return merged_df


