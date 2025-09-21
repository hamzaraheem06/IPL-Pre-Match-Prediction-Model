import pandas as pd
from collections import deque


from collections import defaultdict
import pandas as pd

def compute_rolling_features_balls(df, prior_matches=20):
    """
    Computes all specified rolling features for each team and match,
    including phase-wise scores, composite indices, and player form metrics.

    Args:
        df (pd.DataFrame): The match-level data with innings details.
        prior_matches (int): Number of previous matches to consider for rolling averages.

    Returns:
        pd.DataFrame: The original dataframe with added rolling features.
    """
    df = df.copy().sort_values("match_id").reset_index(drop=True)

    # Initialize defaultdicts for historical stats
    team_stats = defaultdict(lambda: {'batting': [], 'bowling': []})

    # Storage for the new features
    rolling_features = []

    for idx, row in df.iterrows():
        match_id = row['match_id']
        t1, t2 = row['team1'], row['team2']

        # --- 1. Compute pre-match (leak-free) rolling features ---
        current_features = {'match_id': match_id}

        def get_rolling_stats(team_name):
            stats = {'batting': {}, 'bowling': {}}

            # Batting metrics
            batting_hist = pd.DataFrame(team_stats[team_name]['batting']).tail(prior_matches)
            if not batting_hist.empty:
                stats['batting']['avg_pp_runs'] = batting_hist['pp_runs'].mean()
                stats['batting']['avg_mo_runs'] = batting_hist['mo_runs'].mean()
                stats['batting']['avg_do_runs'] = batting_hist['do_runs'].mean()
                stats['batting']['avg_pp_wickets'] = batting_hist['pp_wickets'].mean()
                stats['batting']['avg_mo_wickets'] = batting_hist['mo_wickets'].mean()
                stats['batting']['avg_do_wickets'] = batting_hist['do_wickets'].mean()
                stats['batting']['avg_run_rate'] = batting_hist['run_rate'].mean()
                stats['batting']['avg_boundaries'] = batting_hist['boundaries'].mean()
                stats['batting']['avg_dot_rate'] = batting_hist['dot_ball_rate'].mean()
            else:
                for k in ['avg_pp_runs', 'avg_mo_runs', 'avg_do_runs', 'avg_pp_wickets', 'avg_mo_wickets', 'avg_do_wickets', 'avg_run_rate', 'avg_boundaries', 'avg_dot_rate']:
                    stats['batting'][k] = 0.0

            # Bowling metrics
            bowling_hist = pd.DataFrame(team_stats[team_name]['bowling']).tail(prior_matches)
            if not bowling_hist.empty:
                stats['bowling']['avg_economy_rate'] = bowling_hist['economy_rate'].mean()
                stats['bowling']['avg_wicket_rate'] = bowling_hist['wicket_rate'].mean()
                stats['bowling']['avg_dot_rate'] = bowling_hist['dot_ball_rate'].mean()
            else:
                for k in ['avg_economy_rate', 'avg_wicket_rate', 'avg_dot_rate']:
                    stats['bowling'][k] = 0.0

            return stats

        t1_stats = get_rolling_stats(t1)
        t2_stats = get_rolling_stats(t2)

        # Populate features for team 1 and team 2
        for stat_type in ['batting', 'bowling']:
            for k, v in t1_stats[stat_type].items():
                current_features[f'team1_{stat_type}_{k}'] = v
            for k, v in t2_stats[stat_type].items():
                current_features[f'team2_{stat_type}_{k}'] = v
                current_features[f'team_diff_{stat_type}_{k}'] = t1_stats[stat_type].get(k, 0) - t2_stats[stat_type].get(k, 0)

        # --- 2. Calculate Composite Features ---
        current_features['team1_batting_index'] = (current_features['team1_batting_avg_run_rate'] * 0.5) + \
                                                (current_features['team1_batting_avg_boundaries'] * 0.3) - \
                                                (current_features['team1_batting_avg_dot_rate'] * 0.2)

        current_features['team2_batting_index'] = (current_features['team2_batting_avg_run_rate'] * 0.5) + \
                                                (current_features['team2_batting_avg_boundaries'] * 0.3) - \
                                                (current_features['team2_batting_avg_dot_rate'] * 0.2)

        current_features['batting_index_diff'] = current_features['team1_batting_index'] - current_features['team2_batting_index']

        current_features['team1_bowling_index'] = (current_features['team1_bowling_avg_economy_rate'] * -0.5) + \
                                                 (current_features['team1_bowling_avg_wicket_rate'] * 0.3) + \
                                                 (current_features['team1_bowling_avg_dot_rate'] * 0.2)

        current_features['team2_bowling_index'] = (current_features['team2_bowling_avg_economy_rate'] * -0.5) + \
                                                 (current_features['team2_bowling_avg_wicket_rate'] * 0.3) + \
                                                 (current_features['team2_bowling_avg_dot_rate'] * 0.2)

        current_features['bowling_index_diff'] = current_features['team1_bowling_index'] - current_features['team2_bowling_index']

        rolling_features.append(current_features)

        # --- 3. Update historical stats AFTER the match ---
        # Innings 1 data (team1 batting, team2 bowling)
        innings1_data = row.filter(like='innings1_').to_dict()
        innings1_data = {k.replace('innings1_', ''): v for k, v in innings1_data.items()}

        # Calculate bowling rates from batting data for team2
        balls_bowled_i1 = innings1_data['balls_bowled']
        total_runs_i1 = innings1_data['total_runs']
        total_wickets_i1 = innings1_data['total_wickets']
        dot_balls_i1 = innings1_data['dot_balls']

        bowling_stats_i1 = {
            'economy_rate': (total_runs_i1 / balls_bowled_i1) * 6 if balls_bowled_i1 > 0 else 0,
            'wicket_rate': total_wickets_i1 / balls_bowled_i1 if balls_bowled_i1 > 0 else 0,
            'dot_ball_rate': dot_balls_i1 / balls_bowled_i1 if balls_bowled_i1 > 0 else 0
        }

        team_stats[t1]['batting'].append(innings1_data)
        team_stats[t2]['bowling'].append(bowling_stats_i1)

        # Innings 2 data (team2 batting, team1 bowling)
        innings2_data = row.filter(like='innings2_').to_dict()
        innings2_data = {k.replace('innings2_', ''): v for k, v in innings2_data.items()}

        # Calculate bowling rates from batting data for team1
        balls_bowled_i2 = innings2_data['balls_bowled']
        total_runs_i2 = innings2_data['total_runs']
        total_wickets_i2 = innings2_data['total_wickets']
        dot_balls_i2 = innings2_data['dot_balls']

        bowling_stats_i2 = {
            'economy_rate': (total_runs_i2 / balls_bowled_i2) * 6 if balls_bowled_i2 > 0 else 0,
            'wicket_rate': total_wickets_i2 / balls_bowled_i2 if balls_bowled_i2 > 0 else 0,
            'dot_ball_rate': dot_balls_i2 / balls_bowled_i2 if balls_bowled_i2 > 0 else 0
        }

        team_stats[t2]['batting'].append(innings2_data)
        team_stats[t1]['bowling'].append(bowling_stats_i2)

    # Convert list of dictionaries to a DataFrame and merge with the original data
    rolling_df = pd.DataFrame(rolling_features)
    final_df = pd.merge(df, rolling_df, on='match_id', how='left')

    return final_df

def calculate_venue_features(df):
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


def calculate_toss_stats(matches, window=5):
    """
    Calculates rolling toss-based statistics for each match without data leakage.
    Features include:
        - team1_recent_toss_winrate, team2_recent_toss_winrate
        - team1_recent_toss_bat_rate, team2_recent_toss_bat_rate
        - team1_toss_match_winrate, team2_toss_match_winrate
        - toss_match_winrate_diff
        - venue_toss_winrate
        - team1_lost_toss_winrate, team2_lost_toss_winrate
        - team1_form_toss_boost, team2_form_toss_boost
    """
    # Rolling storage
    toss_win_stats = {}      # team -> {"wins":, "total":}
    toss_bat_stats = {}      # team -> {"bat":, "total":}
    toss_match_stats = {}    # team -> {"wins_after_toss":, "toss_wins":}
    venue_toss_stats = {}    # venue -> {"wins":, "total":}
    lost_toss_stats = {}     # team -> {"wins":, "total":}
    form_toss_stats = {}     # team -> {"wins_with_form":, "total_with_form":, "form_history": deque}

    rows = []

    for _, row in matches.iterrows():
        team1, team2 = row["team1"], row["team2"]
        venue = row["venue"]
        toss_winner = row["toss_winner"]
        toss_decision = row["toss_decision"]
        winner = row["winner"]

        # --- Initialize defaults if team/venue not seen before ---
        for team in [team1, team2]:
            toss_win_stats.setdefault(team, {"wins": 0, "total": 0})
            toss_bat_stats.setdefault(team, {"bat": 0, "total": 0})
            toss_match_stats.setdefault(team, {"wins_after_toss": 0, "toss_wins": 0})
            lost_toss_stats.setdefault(team, {"wins": 0, "total": 0})
            form_toss_stats.setdefault(team, {
                "wins_with_form": 0,
                "total_with_form": 0,
                "form_history": deque(maxlen=window)
            })

        venue_toss_stats.setdefault(venue, {"wins": 0, "total": 0})

        # -------- FEATURES BEFORE MATCH (only past data) -------- #
        # Recent toss winrate
        t1_recent_toss_winrate = toss_win_stats[team1]["wins"] / toss_win_stats[team1]["total"] if toss_win_stats[team1]["total"] > 0 else 0.5
        t2_recent_toss_winrate = toss_win_stats[team2]["wins"] / toss_win_stats[team2]["total"] if toss_win_stats[team2]["total"] > 0 else 0.5

        # Toss bat rate
        t1_recent_bat_rate = toss_bat_stats[team1]["bat"] / toss_bat_stats[team1]["total"] if toss_bat_stats[team1]["total"] > 0 else 0.5
        t2_recent_bat_rate = toss_bat_stats[team2]["bat"] / toss_bat_stats[team2]["total"] if toss_bat_stats[team2]["total"] > 0 else 0.5

        # Winrate after winning toss
        t1_toss_match_winrate = toss_match_stats[team1]["wins_after_toss"] / toss_match_stats[team1]["toss_wins"] if toss_match_stats[team1]["toss_wins"] > 0 else 0.5
        t2_toss_match_winrate = toss_match_stats[team2]["wins_after_toss"] / toss_match_stats[team2]["toss_wins"] if toss_match_stats[team2]["toss_wins"] > 0 else 0.5
        toss_match_winrate_diff = t1_toss_match_winrate - t2_toss_match_winrate

        # Venue toss winrate
        venue_toss_winrate = venue_toss_stats[venue]["wins"] / venue_toss_stats[venue]["total"] if venue_toss_stats[venue]["total"] > 0 else 0.5

        # Lost toss winrate
        t1_lost_toss_winrate = lost_toss_stats[team1]["wins"] / lost_toss_stats[team1]["total"] if lost_toss_stats[team1]["total"] > 0 else 0.5
        t2_lost_toss_winrate = lost_toss_stats[team2]["wins"] / lost_toss_stats[team2]["total"] if lost_toss_stats[team2]["total"] > 0 else 0.5

        # Form-toss boost
        def calc_form_boost(team):
            hist = form_toss_stats[team]["form_history"]
            if not hist:
                return 0.0
            avg_form = sum(hist) / len(hist)
            if form_toss_stats[team]["total_with_form"] == 0:
                return 0.0
            return (form_toss_stats[team]["wins_with_form"] / form_toss_stats[team]["total_with_form"]) - avg_form

        t1_form_toss_boost = calc_form_boost(team1)
        t2_form_toss_boost = calc_form_boost(team2)

        # Save features for this match
        rows.append({
            "team1_recent_toss_winrate": t1_recent_toss_winrate,
            "team2_recent_toss_winrate": t2_recent_toss_winrate,
            "team1_recent_toss_bat_rate": t1_recent_bat_rate,
            "team2_recent_toss_bat_rate": t2_recent_bat_rate,
            "team1_toss_match_winrate": t1_toss_match_winrate,
            "team2_toss_match_winrate": t2_toss_match_winrate,
            "toss_match_winrate_diff": toss_match_winrate_diff,
            "venue_toss_winrate": venue_toss_winrate,
            "team1_lost_toss_winrate": t1_lost_toss_winrate,
            "team2_lost_toss_winrate": t2_lost_toss_winrate,
            "team1_form_toss_boost": t1_form_toss_boost,
            "team2_form_toss_boost": t2_form_toss_boost,
        })

        # -------- UPDATE AFTER MATCH (use current match result) -------- #
        # Toss win/loss
        toss_win_stats[toss_winner]["wins"] += 1
        toss_win_stats[toss_winner]["total"] += 1
        loser = team1 if toss_winner == team2 else team2
        toss_win_stats[loser]["total"] += 1

        # Toss decision
        toss_bat_stats[toss_winner]["total"] += 1
        if toss_decision == "bat":
            toss_bat_stats[toss_winner]["bat"] += 1

        # Toss → match winrate
        toss_match_stats[toss_winner]["toss_wins"] += 1
        if toss_winner == winner:
            toss_match_stats[toss_winner]["wins_after_toss"] += 1

        # Venue toss
        venue_toss_stats[venue]["total"] += 1
        if toss_winner == winner:
            venue_toss_stats[venue]["wins"] += 1

        # Lost toss stats
        if toss_winner != team1:
            lost_toss_stats[team1]["total"] += 1
            if winner == team1:
                lost_toss_stats[team1]["wins"] += 1
        if toss_winner != team2:
            lost_toss_stats[team2]["total"] += 1
            if winner == team2:
                lost_toss_stats[team2]["wins"] += 1

        # Form-toss boost
        for team in [team1, team2]:
            form_toss_stats[team]["form_history"].append(1 if winner == team else 0)
        if toss_winner == winner:
            form_toss_stats[toss_winner]["wins_with_form"] += 1
        form_toss_stats[toss_winner]["total_with_form"] += 1

    return pd.DataFrame(rows)

def add_head_to_head_toss_advantage(df, prior_matches=4):
    """
    Adds leak-free head-to-head toss advantage features:
      - team1_h2h_toss_advantage, team2_h2h_toss_advantage
      - h2h_toss_advantage_diff (team1 - team2)

    prior_matches: Laplace smoothing prior (default=4).
    """
    df = df.copy()
    df = df.reset_index(drop=True)

    # store h2h toss stats: (teamA, teamB) -> {toss_wins, toss_wins_converted}
    h2h_toss_stats = defaultdict(lambda: {"toss_wins": 0, "toss_win_converted": 0})

    t1_adv_list, t2_adv_list = [], []

    prior_converted = prior_matches / 2  # prior ~50% conversion rate

    for _, row in df.iterrows():
        t1, t2 = row["team1"], row["team2"]
        toss_winner = row["toss_winner"]
        winner = row["winner"]

        # --- compute (before updating) ---
        def compute_adv(team, opp):
            stats = h2h_toss_stats[(team, opp)]
            tw, tc = stats["toss_wins"], stats["toss_win_converted"]
            if tw == 0:
                return 0.5  # no history → neutral
            return (tc + prior_converted) / (tw + prior_matches)

        t1_adv = compute_adv(t1, t2)
        t2_adv = compute_adv(t2, t1)
        t1_adv_list.append(t1_adv)
        t2_adv_list.append(t2_adv)

        # --- update AFTER match ---
        if toss_winner == t1:
            h2h_toss_stats[(t1, t2)]["toss_wins"] += 1
            if winner == t1:
                h2h_toss_stats[(t1, t2)]["toss_win_converted"] += 1

        elif toss_winner == t2:
            h2h_toss_stats[(t2, t1)]["toss_wins"] += 1
            if winner == t2:
                h2h_toss_stats[(t2, t1)]["toss_win_converted"] += 1

    # attach features
    df["team1_h2h_toss_advantage"] = t1_adv_list
    df["team2_h2h_toss_advantage"] = t2_adv_list
    df["h2h_toss_advantage_diff"] = df["team1_h2h_toss_advantage"] - df["team2_h2h_toss_advantage"]

    return df


def add_chasing_defending_strength(df):
    """
    Adds chasing and defending strengths for each team based on past matches.
    Also adds preference scores (chasing - defending).
    Separates normal vs pressure matches (Final/Eliminator).
    """
    df = df.copy()

    # --- Normal stats ---
    team_chasing_wins = {}
    team_chasing_matches = {}
    team_defending_wins = {}
    team_defending_matches = {}

    # --- Pressure stats ---
    team_chasing_wins_pressure = {}
    team_chasing_matches_pressure = {}
    team_defending_wins_pressure = {}
    team_defending_matches_pressure = {}

    team1_chasing_strength, team1_defending_strength = [], []
    team2_chasing_strength, team2_defending_strength = [], []
    team1_pref_score, team2_pref_score = [], []

    team1_chasing_strength_pressure, team1_defending_strength_pressure = [], []
    team2_chasing_strength_pressure, team2_defending_strength_pressure = [], []
    team1_pref_score_pressure, team2_pref_score_pressure = [], []

    for _, row in df.iterrows():
        t1, t2, toss_winner, toss_decision, winner, match_type = (
            row["team1"], row["team2"], row["toss_winner"], row["toss_decision"], row["winner"], row["match_type"]
        )

        is_pressure = match_type in ["Final", "Eliminator 1", "Eliminator 2"]

        # --- Get stats function ---
        def get_strengths(team, chasing_wins, chasing_matches, defending_wins, defending_matches):
            chase_strength = chasing_wins.get(team, 0) / chasing_matches.get(team, 0) if chasing_matches.get(team, 0) > 0 else 0.5
            defend_strength = defending_wins.get(team, 0) / defending_matches.get(team, 0) if defending_matches.get(team, 0) > 0 else 0.5
            return chase_strength, defend_strength, chase_strength - defend_strength

        # --- Team1 (normal + pressure) ---
        chase, defend, pref = get_strengths(t1, team_chasing_wins, team_chasing_matches, team_defending_wins, team_defending_matches)
        team1_chasing_strength.append(chase)
        team1_defending_strength.append(defend)
        team1_pref_score.append(pref)

        chase_p, defend_p, pref_p = get_strengths(t1, team_chasing_wins_pressure, team_chasing_matches_pressure, team_defending_wins_pressure, team_defending_matches_pressure)
        team1_chasing_strength_pressure.append(chase_p)
        team1_defending_strength_pressure.append(defend_p)
        team1_pref_score_pressure.append(pref_p)

        # --- Team2 (normal + pressure) ---
        chase, defend, pref = get_strengths(t2, team_chasing_wins, team_chasing_matches, team_defending_wins, team_defending_matches)
        team2_chasing_strength.append(chase)
        team2_defending_strength.append(defend)
        team2_pref_score.append(pref)

        chase_p, defend_p, pref_p = get_strengths(t2, team_chasing_wins_pressure, team_chasing_matches_pressure, team_defending_wins_pressure, team_defending_matches_pressure)
        team2_chasing_strength_pressure.append(chase_p)
        team2_defending_strength_pressure.append(defend_p)
        team2_pref_score_pressure.append(pref_p)

        # --- Update stats after match ---
        if toss_winner == t1:
            first_batting = t1 if toss_decision == "bat" else t2
        else:
            first_batting = t2 if toss_decision == "bat" else t1

        chasing_team = t1 if first_batting == t2 else t2
        defending_team = first_batting

        # Normal update
        team_chasing_matches[chasing_team] = team_chasing_matches.get(chasing_team, 0) + 1
        if winner == chasing_team:
            team_chasing_wins[chasing_team] = team_chasing_wins.get(chasing_team, 0) + 1

        team_defending_matches[defending_team] = team_defending_matches.get(defending_team, 0) + 1
        if winner == defending_team:
            team_defending_wins[defending_team] = team_defending_wins.get(defending_team, 0) + 1

        # Pressure update
        if is_pressure:
            team_chasing_matches_pressure[chasing_team] = team_chasing_matches_pressure.get(chasing_team, 0) + 1
            if winner == chasing_team:
                team_chasing_wins_pressure[chasing_team] = team_chasing_wins_pressure.get(chasing_team, 0) + 1

            team_defending_matches_pressure[defending_team] = team_defending_matches_pressure.get(defending_team, 0) + 1
            if winner == defending_team:
                team_defending_wins_pressure[defending_team] = team_defending_wins_pressure.get(defending_team, 0) + 1

    # --- Assign back ---
    df["team1_chasing_strength"] = team1_chasing_strength
    df["team1_defending_strength"] = team1_defending_strength
    df["team2_chasing_strength"] = team2_chasing_strength
    df["team2_defending_strength"] = team2_defending_strength
    df["team1_pref_score"] = team1_pref_score
    df["team2_pref_score"] = team2_pref_score
    df["pref_score_diff"] = df["team1_pref_score"] - df["team2_pref_score"]
    df["chasing_strength_diff"] = df["team1_chasing_strength"] - df["team2_chasing_strength"]
    df["defending_strength_diff"] = df["team1_defending_strength"] - df["team2_defending_strength"]

    # --- Pressure stats ---
    df["team1_chasing_strength_pressure"] = team1_chasing_strength_pressure
    df["team1_defending_strength_pressure"] = team1_defending_strength_pressure
    df["team2_chasing_strength_pressure"] = team2_chasing_strength_pressure
    df["team2_defending_strength_pressure"] = team2_defending_strength_pressure
    df["team1_pref_score_pressure"] = team1_pref_score_pressure
    df["team2_pref_score_pressure"] = team2_pref_score_pressure
    df["pref_score_diff_pressure"] = df["team1_pref_score_pressure"] - df["team2_pref_score_pressure"]

    return df



def add_diff_features(df):
    """
    Add *_diff columns (team1_x - team2_x) for all matching team1_/team2_ pairs.
    Keeps the original columns.
    """

    # Find team1_ / team2_ column pairs
    team1_cols = [c for c in df.columns if c.startswith("team1_")]
    team2_cols = [c for c in df.columns if c.startswith("team2_")]

    # Match by suffix
    suffixes = set([c.replace("team1_", "") for c in team1_cols]) & \
               set([c.replace("team2_", "") for c in team2_cols])

    for suf in suffixes:
        col1 = f"team1_{suf}"
        col2 = f"team2_{suf}"
        diff_col = f"{suf}_diff"
        df[diff_col] = df[col1] - df[col2]

    return df


def add_venue_features(df):
    """
    Adds rolling venue-level features (no team-specific leakage).
    Features:
        - venue_avg_target_run
        - venue_chasing_win_rate
        - venue_defending_win_rate
    """
    df = df.copy()

    # Rolling dictionaries
    venue_runs = {}
    venue_matches = {}
    venue_chasing_wins = {}
    venue_chasing_matches = {}
    venue_defending_wins = {}
    venue_defending_matches = {}

    avg_target_runs = []
    chasing_win_rates = []
    defending_win_rates = []

    for _, row in df.iterrows():
        venue = row["venue"]
        winner = row["winner"]
        toss_decision, toss_winner = row["toss_decision"], row["toss_winner"]
        team1, team2 = row["team1"], row["team2"]

        # ====== Venue average first innings score ======
        if venue in venue_runs:
            avg_target_runs.append(
                venue_runs[venue] / max(1, venue_matches[venue])
            )
        else:
            avg_target_runs.append(0.0)

        # ====== Venue chasing win rate ======
        if venue in venue_chasing_wins:
            chasing_win_rates.append(
                venue_chasing_wins[venue] / max(1, venue_chasing_matches[venue])
            )
        else:
            chasing_win_rates.append(0.5)

        # ====== Venue defending win rate ======
        if venue in venue_defending_wins:
            defending_win_rates.append(
                venue_defending_wins[venue] / max(1, venue_defending_matches[venue])
            )
        else:
            defending_win_rates.append(0.5)

        # ====== Update after match ======
        # Update venue scoring stats
        if pd.notnull(row["target_runs"]):  # first innings runs
            venue_runs[venue] = venue_runs.get(venue, 0) + row["target_runs"]
        venue_matches[venue] = venue_matches.get(venue, 0) + 1

        # Chasing or Defending update
        if toss_decision == "field":
            # chasing team is toss_winner, defending is opponent
            chasing_team = toss_winner
            defending_team = team1 if toss_winner == team2 else team2

            venue_chasing_matches[venue] = venue_chasing_matches.get(venue, 0) + 1
            venue_defending_matches[venue] = venue_defending_matches.get(venue, 0) + 1

            if winner == chasing_team:
                venue_chasing_wins[venue] = venue_chasing_wins.get(venue, 0) + 1
            elif winner == defending_team:
                venue_defending_wins[venue] = venue_defending_wins.get(venue, 0) + 1
        else:
            # toss_decision == "bat" → toss winner bats first, so they defend
            defending_team = toss_winner
            chasing_team = team1 if toss_winner == team2 else team2

            venue_chasing_matches[venue] = venue_chasing_matches.get(venue, 0) + 1
            venue_defending_matches[venue] = venue_defending_matches.get(venue, 0) + 1

            if winner == chasing_team:
                venue_chasing_wins[venue] = venue_chasing_wins.get(venue, 0) + 1
            elif winner == defending_team:
                venue_defending_wins[venue] = venue_defending_wins.get(venue, 0) + 1

    # Add new columns
    df["venue_avg_target_run"] = avg_target_runs
    df["venue_chasing_win_rate"] = chasing_win_rates
    df["venue_defending_win_rate"] = defending_win_rates

    return df

selected_features = [

# ---------------------------
# Team Strength & Form (historic only)
# ---------------------------
"team1_recent_form",
"team2_recent_form",
"team1_streak",
"team2_streak",
"win_ratio_diff",
"recent_form_diff",
"streak_diff",

# ---------------------------
# Head-to-Head (past matches only)
# ---------------------------
"head_to_head_winrate",

# ---------------------------
# Toss-related rolling features
# ---------------------------
"toss_match_winrate_diff",
"venue_toss_winrate",
"team1_h2h_toss_advantage",
"team2_h2h_toss_advantage",
"h2h_toss_advantage_diff",
"recent_toss_winrate_diff",
"lost_toss_winrate_diff",
"form_toss_boost_diff",
"recent_toss_bat_rate_diff",

# ---------------------------
# Chasing / Defending Strength (historic)
# ---------------------------
"pref_score_diff",
"chasing_strength_diff",
"defending_strength_diff",
"team1_defending_strength",
"team2_chasing_strength",
"team1_defending_strength_pressure",
"team2_chasing_strength_pressure",

# ---------------------------
# Pressure-adjusted variants
# ---------------------------
"chasing_strength_pressure_diff",
"defending_strength_pressure_diff",
"pref_score_pressure_diff",

# ---------------------------
# Venue-level historic stats
# ---------------------------
"venue_avg_target_run",
"venue_chasing_win_rate",
"venue_bat_first_winrate",
"venue_chase_winrate",
"venue_winrate_diff",
"venue_toss_bias",

# ---------------------------
# Team Batting Rolling Averages (from ball-by-ball)
# ---------------------------
"team_diff_batting_avg_pp_runs",
"team_diff_batting_avg_mo_runs",
"team_diff_batting_avg_do_runs",
"team_diff_batting_avg_pp_wickets",
"team_diff_batting_avg_mo_wickets",
"team_diff_batting_avg_do_wickets",
"team_diff_batting_avg_run_rate",
"team_diff_batting_avg_boundaries",
"team_diff_batting_avg_dot_rate",

# ---------------------------
# Team Bowling Rolling Averages (from ball-by-ball)
# ---------------------------
"team_diff_bowling_avg_economy_rate",
"team_diff_bowling_avg_wicket_rate",
"team_diff_bowling_avg_dot_rate",

# ---------------------------
# Composite Indexes
# ---------------------------
"batting_index_diff",
"bowling_index_diff",

# ---------------------------
# Toss Decision One-Hot
# ---------------------------
"toss_decision_bat",
"toss_decision_field",
]

