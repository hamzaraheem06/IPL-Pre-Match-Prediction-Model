#!/usr/bin/env python3
"""Debug why factors are identical across team combinations"""

from app import transform_input
import pandas as pd

def debug_identical_factors():
    print('=== Debugging Identical Factors Issue ===')
    
    # Test two very different teams
    team_combos = [
        ('mi', 'csk', 'Mumbai Indians vs Chennai Super Kings'),
        ('rcb', 'kkr', 'Royal Challengers Bangalore vs Kolkata Knight Riders')
    ]
    
    venue = 'wankhede'
    
    for i, (team1, team2, description) in enumerate(team_combos):
        print(f'\n=== Test {i+1}: {description} ===')
        
        try:
            # Get the features and factors
            features, factors = transform_input({
                'team1Id': team1,
                'team2Id': team2, 
                'venueId': venue,
                'tossWinner': team1,
                'tossDecision': 'bat'
            })
            
            print(f'Factors: {factors}')
            
            # Check the raw feature values that should be different
            critical_features = [
                'head_to_head_winrate',
                'recent_form_diff',
                'team1_recent_form', 
                'team2_recent_form',
                'venue_team1_winrate',
                'venue_team2_winrate'
            ]
            
            print('Critical feature values:')
            for feature in critical_features:
                if feature in features.columns:
                    value = features[feature].iloc[0]
                    print(f'  {feature}: {value:.6f}')
                else:
                    print(f'  {feature}: MISSING')
                    
        except Exception as e:
            print(f'Error: {e}')
    
    print('\n=== Root Cause Analysis ===')
    print('If all factors are identical, the issue could be:')
    print('1. 🔍 Feature engineering always uses the LAST row of historical data')
    print('2. 🔍 The new match data is not being differentiated by team names')
    print('3. 🔍 Rolling calculations are not team-specific')
    print('4. 🔍 The prediction row selection is wrong')
    
    # Let's check the prediction row creation
    print('\n=== Checking Prediction Row Creation ===')
    test_new_match_creation()

def test_new_match_creation():
    """Test if new match entries are created correctly"""
    print('Testing new match entry creation...')
    
    from app import team_mapping, venue_mapping
    
    # Test two different inputs
    inputs = [
        {'team1Id': 'mi', 'team2Id': 'csk', 'venueId': 'wankhede', 'tossWinner': 'mi', 'tossDecision': 'bat'},
        {'team1Id': 'rcb', 'team2Id': 'kkr', 'venueId': 'wankhede', 'tossWinner': 'rcb', 'tossDecision': 'bat'}
    ]
    
    for i, input_data in enumerate(inputs):
        print(f'\nInput {i+1}: {input_data}')
        
        # Simulate the new match creation logic from transform_input
        team1_name = team_mapping.get(input_data.get('team1Id', '').lower())
        team2_name = team_mapping.get(input_data.get('team2Id', '').lower()) 
        venue_name = venue_mapping.get(input_data.get('venueId', '').lower())
        toss_winner_name = team_mapping.get(input_data.get('tossWinner', '').lower())
        toss_decision = input_data.get('tossDecision', 'bat').lower()
        
        new_match = {
            'match_id': 999999,
            'season': 2024,
            'match_type': 'League', 
            'venue': venue_name,
            'team1': team1_name,
            'team2': team2_name,
            'toss_winner': toss_winner_name,
            'toss_decision': toss_decision,
            'winner': team1_name,  # This might be the issue!
            'result': 'runs'
        }
        
        print(f'Created match entry:')
        for key, value in new_match.items():
            print(f'  {key}: {value}')
    
    print('\n❗ POTENTIAL ISSUE FOUND:')
    print('The new match entry has winner = team1_name (always team1)')
    print('This means the prediction row always thinks team1 won!')
    print('This could affect rolling calculations and recent form.')

if __name__ == '__main__':
    debug_identical_factors()