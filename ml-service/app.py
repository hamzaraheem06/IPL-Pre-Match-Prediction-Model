# ml-service/app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from collections import defaultdict, deque

# Import data loading and processing functions
from clean_balls_data import summarize_match_data, pivot_match_data, normalize_team as normalize_team_balls
from clean_match_data import normalize_team as normalize_team_match, normalize_match_type  
from features_engineering_encoding import (
    calculate_rolling_stats,
    compute_rolling_features_balls,  
    calculate_toss_stats, 
    add_head_to_head_toss_advantage, 
    add_chasing_defending_strength,
    add_diff_features,
    add_venue_features,
    selected_features
)
from historical_stats import stats_calculator



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

        final_balls_df = final_balls_df[final_balls_df['season_id'] != 2025 or final_balls_df['season_id'] != "2025"]
        
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

def compute_matchup_features(team1_name, team2_name, venue_name, toss_winner_name, toss_decision, historical_data):
    """
    Compute all matchup features for a given pair of teams/venue/toss setup.
    Uses rolling + aggregated stats functions instead of dummy values.
    """
    try:
        # Step 1: Filter historical data for these two teams
        matchup_data = historical_data[
            ((historical_data['team1'] == team1_name) & (historical_data['team2'] == team2_name)) |
            ((historical_data['team1'] == team2_name) & (historical_data['team2'] == team1_name))
        ].copy()

        if matchup_data.empty:
            print("⚠️ No historical matches found for this matchup. Returning defaults.")
            return {f: 0.5 for f in selected_features}

        # Step 2: Run the feature engineering pipeline
        matchup_data = calculate_rolling_stats(matchup_data)
        summary = summarize_match_data(matchup_data)
        pivoted = pivot_match_data(summary)
        matchup_data = compute_rolling_features_balls(pivoted)

        data_team_toss = calculate_toss_stats(matchup_data)
        matchup_data = pd.concat([matchup_data, data_team_toss], axis=1)
        matchup_data = add_head_to_head_toss_advantage(matchup_data)
        matchup_data = add_chasing_defending_strength(matchup_data)
        matchup_data = add_diff_features(matchup_data)
        matchup_data = add_venue_features(matchup_data)

        # Step 3: Take the last row (latest match-based stats)
        latest_features = matchup_data.iloc[-1].to_dict()

        # Step 4: Add toss_decision one-hot encoding
        latest_features['toss_decision_bat'] = 1 if toss_decision == "bat" else 0
        latest_features['toss_decision_field'] = 1 if toss_decision == "field" else 0

        # Step 5: Extract only selected_features
        feature_vector = {f: latest_features.get(f, 0) for f in selected_features}

        return feature_vector

    except Exception as e:
        print(f"❌ Error in compute_matchup_features: {e}")
        return {f: 0.5 for f in selected_features}


def transform_input(raw_input: dict):
    """Transform user input from UI into features for ML model"""
    try:
        # Map UI IDs to model format
        team1_name = team_mapping.get(raw_input.get('team1Id', '').lower())
        team2_name = team_mapping.get(raw_input.get('team2Id', '').lower())
        venue_name = venue_mapping.get(raw_input.get('venueId', '').lower())
        toss_winner_name = team_mapping.get(raw_input.get('tossWinner', '').lower())
        toss_decision = raw_input.get('tossDecision', 'bat').lower()
        
        if not all([team1_name, team2_name, venue_name, toss_winner_name]):
            raise ValueError("Invalid team or venue IDs provided")
        
        # Use targeted feature computation instead of full pipeline
        if historical_data is not None:
            # Compute features specific to this matchup
            matchup_features = compute_matchup_features(
                team1_name, team2_name, venue_name, toss_winner_name, toss_decision, historical_data
            )
            
            if matchup_features is None:
                raise ValueError("Failed to compute matchup features")
                
            # Create DataFrame with features in correct order
            feature_data = pd.DataFrame([matchup_features])
            
            # Extract factors from the computed features
            factors = {
                "venueAdvantage": float(matchup_features.get('venue_winrate_diff', 0)),
                "tossDecision": float(matchup_features.get('toss_match_winrate_diff', 0)),
                "recentForm": float(matchup_features.get('recent_form_diff', 0)),
                "headToHead": float(matchup_features.get('head_to_head_winrate', 0.5))
            }
            
            # Convert to percentages and cap values
            factors = {
                "venueAdvantage": max(-50, min(50, factors["venueAdvantage"] * 100)),
                "tossDecision": max(-30, min(30, factors["tossDecision"] * 100)),
                "recentForm": max(-40, min(40, factors["recentForm"] * 100)),
                "headToHead": max(-60, min(60, (factors["headToHead"] - 0.5) * 200))  # Center around 0.5 and scale to percentage
            }
            
            # Ensure we have all required features
            missing_features = [f for f in selected_features if f not in feature_data.columns]
            if missing_features:
                print(f"⚠️ Warning: {len(missing_features)} features missing from targeted computation: {missing_features[:3]}...")
                for feature in missing_features:
                    feature_data[feature] = 0.0
            
            # Select features in the correct order
            feature_data = feature_data[selected_features]
            
            print(f"✅ Targeted computation: {len(selected_features)}/{len(selected_features)} features")
            print(f"🎯 Factors: Venue:{factors['venueAdvantage']:.1f}%, H2H:{factors['headToHead']:.1f}%, Form:{factors['recentForm']:.1f}%, Toss:{factors['tossDecision']:.1f}%")
            
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

class HeadToHeadResponse(BaseModel):
    team1Id: str
    team2Id: str
    totalMatches: int
    team1Wins: int
    team2Wins: int

class ImpactPlayer(BaseModel):
    name: str
    role: str
    impactScore: float
    initials: str

class TeamStatsResponse(BaseModel):
    teamId: str
    powerplayAvg: float
    deathOversEconomy: float
    recentForm: List[bool]
    impactPlayers: List[ImpactPlayer]

class VenueStatResponse(BaseModel):
    venueId: str
    teamId: str
    matches: int
    wins: int
    winRate: float

class VenueDetailsResponse(BaseModel):
    avgFirstInnings: int
    boundaryPercentage: float
    sixRate: float

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

# Historical Stats Endpoints
@app.get("/head-to-head/{team1_id}/{team2_id}", response_model=HeadToHeadResponse)
def get_head_to_head_stats(team1_id: str, team2_id: str):
    """Get historical head-to-head statistics between two teams"""
    try:
        stats = stats_calculator.get_head_to_head_stats(team1_id, team2_id)
        if stats is None:
            raise HTTPException(status_code=404, detail="Head-to-head stats not found")
        return HeadToHeadResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching head-to-head stats: {e}")

@app.get("/team-stats/{team_id}", response_model=TeamStatsResponse)
def get_team_stats(team_id: str):
    """Get comprehensive team statistics"""
    try:
        stats = stats_calculator.get_team_stats(team_id)
        if stats is None:
            raise HTTPException(status_code=404, detail="Team stats not found")
        return TeamStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching team stats: {e}")

@app.get("/venue-stats/{venue_id}", response_model=List[VenueStatResponse])
def get_venue_stats(venue_id: str):
    """Get venue statistics for all teams"""
    try:
        stats = stats_calculator.get_venue_stats(venue_id)
        return [VenueStatResponse(**stat) for stat in stats]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching venue stats: {e}")

@app.get("/venue-details/{venue_id}", response_model=VenueDetailsResponse)
def get_venue_details(venue_id: str):
    """Get venue details including batting conditions"""
    try:
        details = stats_calculator.get_venue_details(venue_id)
        if details is None:
            raise HTTPException(status_code=404, detail="Venue details not found")
        return VenueDetailsResponse(**details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching venue details: {e}")
