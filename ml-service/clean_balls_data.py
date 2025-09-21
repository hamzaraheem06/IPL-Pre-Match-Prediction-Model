import pandas as pd

ball_data = pd.read_csv("data/ball_by_ball_data.csv")

# Drop unused cols
ball_data.drop(columns=["non_striker", "fielders_involved", "wicket_kind", "player_out"], inplace=True)

bool_cols = ["is_wide_ball", "is_no_ball", "is_leg_bye", "is_bye", "is_penalty", "is_super_over", "is_wicket"]
ball_data[bool_cols] = ball_data[bool_cols].astype(int)

# Sort for rolling calculations
balls = ball_data.sort_values(["season_id", "match_id", "innings", "over_number", "ball_number"])

def summarize_match_data(df_balls):
    """
    Converts ball-by-ball data into match-level statistics.

    Args:
        df_balls (pd.DataFrame): The ball-by-ball dataframe.

    Returns:
        pd.DataFrame: A new dataframe with one row per innings per match,
                      summarizing key performance indicators.
    """

    # Calculate key aggregates for each innings of each match
    summary_df = df_balls.groupby(['match_id', 'innings', 'team_batting', 'team_bowling']).apply(lambda x: pd.Series({
        'total_runs': x['total_runs'].sum(),
        'total_wickets': x['is_wicket'].sum(),
        'balls_bowled': len(x),

        # Powerplay stats (Overs 1-6)
        'pp_runs': x[x['over_number'] <= 6]['total_runs'].sum(),
        'pp_wickets': x[x['over_number'] <= 6]['is_wicket'].sum(),

        # Middle overs stats (Overs 7-15)
        'mo_runs': x[(x['over_number'] > 6) & (x['over_number'] <= 15)]['total_runs'].sum(),
        'mo_wickets': x[(x['over_number'] > 6) & (x['over_number'] <= 15)]['is_wicket'].sum(),

        # Death overs stats (Overs 16-20)
        'do_runs': x[x['over_number'] > 15]['total_runs'].sum(),
        'do_wickets': x[x['over_number'] > 15]['is_wicket'].sum(),

        # Other important stats
        'extras_runs': x['extras'].sum(),
        'dot_balls': (x['total_runs'] == 0).sum(),
        'boundaries': (x['batter_runs'].isin([4, 6])).sum(),
    })).reset_index()

    # Calculate rates and percentages
    summary_df['run_rate'] = (summary_df['total_runs'] / summary_df['balls_bowled']) * 6
    summary_df['economy_rate'] = (summary_df['total_runs'] / summary_df['balls_bowled']) * 6
    summary_df['dot_ball_rate'] = summary_df['dot_balls'] / summary_df['balls_bowled']
    summary_df['boundary_rate'] = summary_df['boundaries'] / summary_df['balls_bowled']

    return summary_df

def pivot_match_data(summary_df):
    """
    Pivots the summarized match data (2 rows per match) into a single row per match.

    Args:
        summary_df (pd.DataFrame): The dataframe with one row per innings per match.

    Returns:
        pd.DataFrame: A new dataframe with one row per match, containing stats
                      for both innings in separate columns.
    """

    # Separate data for innings 1 and innings 2
    innings1_df = summary_df[summary_df['innings'] == 1].copy()
    innings2_df = summary_df[summary_df['innings'] == 2].copy()

    # Drop redundant columns from both dataframes before merging
    innings1_df = innings1_df.drop(columns=['innings', 'team_bowling'])
    innings2_df = innings2_df.drop(columns=['innings', 'team_bowling'])

    # Rename columns to distinguish between innings 1 and 2
    innings1_df = innings1_df.rename(columns={col: f'innings1_{col}' for col in innings1_df.columns if col not in ['match_id', 'team_batting']})
    innings2_df = innings2_df.rename(columns={col: f'innings2_{col}' for col in innings2_df.columns if col not in ['match_id', 'team_batting']})

    # Rename team_batting to team1 and team2
    innings1_df = innings1_df.rename(columns={'team_batting': 'team1'})
    innings2_df = innings2_df.rename(columns={'team_batting': 'team2'})

    # Merge the two dataframes on match_id
    final_df = pd.merge(innings1_df, innings2_df, on='match_id', how='left')

    # Reorder columns for clarity
    final_df = final_df.reindex(columns=['match_id', 'team1', 'team2'] + [col for col in final_df.columns if col not in ['match_id', 'team1', 'team2']])

    # Handle cases where an innings might not have been completed
    final_df = final_df.fillna(0)

    return final_df

########## Cleaning team names values

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