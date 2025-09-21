# ml-service/app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any
import os
from collections import defaultdict, deque

# Import data loading and processing functions
from clean_balls_data import summarize_match_data, pivot_match_data, normalize_team as normalize_team_balls
from clean_match_data import normalize_team as normalize_team_match, normalize_match_type
from features_engineering_encoding import (
    compute_rolling_features_balls, 
    calculate_venue_features, 
    calculate_toss_stats, 
    add_head_to_head_toss_advantage, 
    add_chasing_defending_strength,
    add_diff_features,
    add_venue_features,
    selected_features
)

# Load and prepare data once at startup
def load_and_process_data():
    """Load and process historical data for feature engineering"""
    try:
        # Load raw data
        match_data = pd.read_csv("data/match_data.csv")
        ball_data = pd.read_csv("data/ball_by_ball_data.csv")
        
        # Clean match data
        match_data = match_data.drop(columns=["Unnamed: 0", "city", "method"], errors='ignore')
        match_data = match_data.dropna()

        match_data = match_data[match_data['source'] == 'train']
        
        # Normalize match types
        match_data.loc[:, "match_type"] = match_data["match_type"].apply(normalize_match_type)
        
        # Normalize team names for match data
        for col in ["team1", "team2", "toss_winner", "winner"]:
            match_data.loc[:, col] = match_data[col].apply(normalize_team_match)
        
        # Remove rows with None values (defunct teams)
        match_data = match_data.dropna()
        
        # Clean string columns
        match_data = match_data.copy()
        match_data["toss_decision"] = match_data["toss_decision"].str.lower()
        match_data["result"] = match_data["result"].str.lower()
        
        # Drop date column and rename id to match_id
        match_data = match_data.drop(columns=["date"], errors='ignore')
        match_data = match_data.rename(columns={'id': 'match_id'})
        
        # Clean ball data
        ball_data = ball_data.drop(columns=["non_striker", "fielders_involved", "wicket_kind", "player_out"], errors='ignore')
        bool_cols = ["is_wide_ball", "is_no_ball", "is_leg_bye", "is_bye", "is_penalty", "is_super_over", "is_wicket"]
        for col in bool_cols:
            if col in ball_data.columns:
                ball_data[col] = ball_data[col].astype(int)
        
        # Normalize team names for ball data
        for col in ["team_batting", "team_bowling"]:
            if col in ball_data.columns:
                ball_data[col] = ball_data[col].apply(normalize_team_balls)
        
        # Remove rows with None values
        ball_data = ball_data.dropna()
        
        # Sort ball data
        ball_data = ball_data.sort_values(["season_id", "match_id", "innings", "over_number", "ball_number"])
        
        # Summarize match data from ball-by-ball
        summary_df = summarize_match_data(ball_data)
        final_balls_df = pivot_match_data(summary_df)
        
        # Merge match and ball data - we need to implement this properly without encoders
        # Drop team columns from ball data that conflict with match data
        final_balls_clean = final_balls_df.drop(columns=['team1','team2'], errors='ignore')
        
        # Merge on match_id
        merged_df = match_data.merge(final_balls_clean, on='match_id', how='left', sort=False)
        
        return merged_df
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

# Load historical data
historical_data = load_and_process_data()

def create_team_venue_mappings():
    """Create mappings for teams and venues from UI IDs to model format"""
    # Team mappings (UI ID to normalized name)
    team_mapping = {
        "csk": "Chennai Super Kings",
        "mi": "Mumbai Indians", 
        "rcb": "Royal Challengers Bengaluru",
        "kkr": "Kolkata Knight Riders",
        "dc": "Delhi Capitals",
        "rr": "Rajasthan Royals",
        "pbks": "Punjab Kings",
        "srh": "Sunrisers Hyderabad",
        "gt": "Gujarat Titans",
        "lsg": "Lucknow Super Giants"
    }
    
    # Venue mappings (simplified - you may need to expand this)
    venue_mapping = {
        "wankhede": "Wankhede Stadium",
        "eden": "Eden Gardens",
        "chinnaswamy": "M Chinnaswamy Stadium",
        "chepauk": "MA Chidambaram Stadium, Chepauk",
        "kotla": "Feroz Shah Kotla",
        "sawai": "Sawai Mansingh Stadium",
        "mohali": "Punjab Cricket Association Stadium, Mohali",
        "uppal": "Rajiv Gandhi International Stadium, Uppal",
        "narendra": "Narendra Modi Stadium",
        "ekana": "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium"
    }
    
    return team_mapping, venue_mapping

team_mapping, venue_mapping = create_team_venue_mappings()

def transform_input(raw_input: dict):
    """Transform user input from UI into features for ML model"""
    try:
        # Map UI IDs to model format
        team1_name = team_mapping.get(raw_input.get('team1Id', '').lower())
        team2_name = team_mapping.get(raw_input.get('team2Id', '').lower())
        venue_name = venue_mapping.get(raw_input.get('venueId', '').lower())
        toss_winner_name = team_mapping.get(raw_input.get('tossWinner', '').lower())
        toss_decision = raw_input.get('tossDecision', 'bat').lower()
        season = raw_input.get('season', 2024)
        
        if not all([team1_name, team2_name, venue_name, toss_winner_name]):
            raise ValueError("Invalid team or venue IDs provided")
        
        # Create a new match entry
        new_match = {
            'match_id': 999999,  # Dummy match ID
            'season': season,
            'match_type': 'League',
            'venue': venue_name,
            'team1': team1_name,
            'team2': team2_name,
            'toss_winner': toss_winner_name,
            'toss_decision': toss_decision,
            'winner': team1_name,  # Dummy winner (not used in prediction)
            'result': 'runs',
            'target_runs': 160,  # Average target
            'target_overs': 20,
            'super_over': 'N',
            'source': 'train'
        }
        
        # Add dummy innings data (not used in selected features but needed for pipeline)
        innings_cols = [
            'total_runs', 'total_wickets', 'balls_bowled', 'pp_runs', 'pp_wickets',
            'mo_runs', 'mo_wickets', 'do_runs', 'do_wickets', 'extras_runs',
            'dot_balls', 'boundaries', 'run_rate', 'economy_rate', 'dot_ball_rate', 'boundary_rate'
        ]
        
        for innings in [1, 2]:
            for col in innings_cols:
                new_match[f'innings{innings}_{col}'] = 0
                
        # Add the new match to historical data
        if historical_data is not None:
            # Convert new match to DataFrame
            new_match_df = pd.DataFrame([new_match])
            
            # Combine with historical data
            combined_data = pd.concat([historical_data, new_match_df], ignore_index=True)
            combined_data = combined_data.sort_values(["season", "match_id"]).reset_index(drop=True)
            
            # Apply all feature engineering steps
            data_with_rolling = compute_rolling_features_balls(combined_data)
            data_with_venue_team = calculate_venue_features(data_with_rolling)
            data_with_toss = calculate_toss_stats(data_with_venue_team)
            data_with_toss = pd.concat([data_with_venue_team, data_with_toss], axis=1)
            
            # Handle season formatting
            data_with_toss["season"] = data_with_toss["season"].replace({"2020/21": "2020", "2009/10": "2010", "2007/08": "2008"})
            data_with_toss["season"] = pd.to_numeric(data_with_toss["season"], errors='coerce').astype('Int64')
            
            # Add more features
            data_with_h2h_toss = add_head_to_head_toss_advantage(data_with_toss)
            data_with_chase_defend = add_chasing_defending_strength(data_with_h2h_toss)
            data_with_diff = add_diff_features(data_with_chase_defend)
            data_with_venue_features = add_venue_features(data_with_diff)
            
            # Create target column (not used for prediction)
            data_with_venue_features["target"] = (data_with_venue_features["team1"] == data_with_venue_features["winner"]).astype(int)
            
            # Fill NaN values
            final_data = data_with_venue_features.fillna(0)
            
            # Create toss decision one-hot encoding
            final_data["toss_decision_bat"] = (final_data["toss_decision"] == "bat").astype(int)
            final_data["toss_decision_field"] = (final_data["toss_decision"] == "field").astype(int)
            
            # Get the last row (our prediction row)
            prediction_row = final_data.iloc[-1:]
            
            # Select only the features needed for the model
            feature_data = prediction_row[selected_features].copy()
            print(feature_data)
            
            # Create factors for explanation
            factors = {
                "venueAdvantage": float(feature_data.get('venue_team1_winrate', [0])[0] - feature_data.get('venue_team2_winrate', [0])[0]) if 'venue_team1_winrate' in feature_data.columns else 0,
                "tossDecision": float(feature_data.get('toss_match_winrate_diff', [0])[0]) if 'toss_match_winrate_diff' in feature_data.columns else 0,
                "recentForm": float(feature_data.get('recent_form_diff', [0])[0]) if 'recent_form_diff' in feature_data.columns else 0,
                "headToHead": float(feature_data.get('head_to_head_winrate', [0])[0]) if 'head_to_head_winrate' in feature_data.columns else 0
            }
            
            return feature_data, factors
        else:
            # Fallback if historical data loading failed
            dummy_features = pd.DataFrame([{col: 0.0 for col in selected_features}])
            factors = {"venueAdvantage": 0, "tossDecision": 0, "recentForm": 0, "headToHead": 0}
            return dummy_features, factors
            
    except Exception as e:
        print(f"Error in transform_input: {e}")
        # Return dummy data in case of error
        dummy_features = pd.DataFrame([{col: 0.0 for col in selected_features}])
        factors = {"venueAdvantage": 0, "tossDecision": 0, "recentForm": 0, "headToHead": 0}
        return dummy_features, factors

app = FastAPI(title="Cricket ML Service (FastAPI)")

# allow Node server (and later other deploys) to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths to model/encoders
MODEL_PATH = "catboost_model.pkl"            # change if different filename
ENCODERS_PATH = "label_encoders.pkl"         # optional

# Load model at startup
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load model at '{MODEL_PATH}': {e}")

try:
    label_encoders = joblib.load(ENCODERS_PATH)
except Exception:
    label_encoders = None

# ---- Request/Response schemas ----
class PredictionRequest(BaseModel):
    team1Id: str
    team2Id: str
    venueId: str
    tossWinner: str
    tossDecision: str

class PredictionResponse(BaseModel):
    team1WinProbability: float
    team2WinProbability: float
    predictedWinner: str
    expectedMargin: str
    factors: Dict[str, float]

# Health endpoint
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictionResponse)
def predict(req: PredictionRequest):
    # 1) Feature engineering
    raw = req.dict()
    try:
        out = transform_input(raw)
        # transform_input can return either DataFrame or (DataFrame, factors_dict)
        if isinstance(out, tuple) and len(out) == 2:
            X_df, factors = out
        else:
            X_df = out
            factors = {
                "venueAdvantage": 0,
                "tossDecision": 0,
                "recentForm": 0,
                "headToHead": 0
            }
        if not isinstance(X_df, pd.DataFrame):
            raise ValueError("transform_input must return a pandas.DataFrame (or (DataFrame, dict))")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature engineering failed: {e}")

    # 2) Prediction: ensure X_df has expected columns and shape
    try:
        proba = model.predict_proba(X_df)[0]  # [prob_class0, prob_class1]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model prediction failed: {e}")

    # NOTE: assume positive class (class 1) corresponds to TEAM1 winning.
    # If your training label was different, adjust these indices accordingly.
    team1_prob = round(float(proba[1] * 100), 1)
    team2_prob = round(float(proba[0] * 100), 1)

    predicted_winner = req.team1Id if team1_prob > team2_prob else req.team2Id
    top_prob = max(team1_prob, team2_prob)
    if top_prob > 65:
        margin = "15-25 runs"
    elif top_prob > 57:
        margin = "5-15 runs"
    else:
        margin = "Close match"

    response = {
        "team1WinProbability": team1_prob,
        "team2WinProbability": team2_prob,
        "predictedWinner": predicted_winner,
        "expectedMargin": f"{'Team 1' if predicted_winner == req.team1Id else 'Team 2'} expected to win by {margin}",
        "factors": factors
    }
    return response
