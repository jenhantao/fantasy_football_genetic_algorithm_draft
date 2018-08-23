import sys # system functions
import os # os functions
import pandas as pd # for reading data
import numpy as np # for numeric operations
import scipy # scientific computing
import time
import copy


def create_new_players(num_players, num_rounds):
    '''
    Randomly create simulated fantasy players
    inputs: number of players and rounds
    outputs: list of fantasy players
    '''
    num_positions = 6 # number of positions
    player_list = []
    for player_number in range(num_players):
        new_player = []
        for round_number in range(num_rounds):
            weights = np.random.random(num_positions) # initialize random weights
            normed_weights = weights/np.sum(weights) # normalize so weights sum to 1
            new_player.append(normed_weights)
    
        player_list.append((new_player))
    return np.array(player_list)

def simulate_draft(rankFrame, fantasy_players, num_rounds):
    '''
    Simulates a draft and returns a list of rosters for each fantasy player
    inputs: rankFrame - DataFrame containing ranks of players
            fantasy_players - list of fantasy players with different strategies
            num_rounds - number of rounds in the draft
    output: team_rosters - roster selected by each fantasy player
    '''
    team_rosters = [[] for x in range(fantasy_players.shape[0])]
        
    drafted_players = set()
    flip = False
    for draft_round in range(num_rounds):
        for player_index in range(fantasy_players.shape[0]):
            if flip:
                player = fantasy_players.shape[0] - player_index - 1
            else:
                player = player_index
            
#             print(draft_round, player)
            # retrieve strategy
            round_strategy = fantasy_players[player,draft_round, :]
            player_score_tuples = []
            # calculate player ranks
            for index, row in rankFrame[~rankFrame['NAME'].isin(drafted_players)].iterrows(): 
                position = row['POSITION']
                position_weight = round_strategy[position_index_dict[position]]
                weighted_player_score = position_weight * float(row['ADP SCORE'])
                player_score_tuples.append((row['NAME'], weighted_player_score, position))
            
            # draft player
            player_score_tuples.sort(key = lambda x: x[1], reverse=True)
            drafted_player = (player_score_tuples[0][0], player_score_tuples[0][2])
            
            team_rosters[player].append(drafted_player)
            drafted_players.add(drafted_player[0])
        if flip == False:
            flip = True
        else:
            flip = False
    return team_rosters

def score_roster(playerScoreDict, fantasy_rosters):
    '''
    returns a list of performances for each fantasy player's team and lineups for each team
    '''
    fantasy_team_performances = []
    fantasy_lineups = []
    for roster in fantasy_rosters:  
        lineup = []
        roster_with_scores = [(x[0], x[1], playerScoreDict[x[0]]) if x[0] in playerScoreDict else (x[0], x[1], 0) for x in roster]
        roster_with_scores.sort(key = lambda x:x[2], reverse=True)
        
        # fill regular roster
        for pos in ['QB', 'WR', 'WR', 'RB', 'RB', 'PK', 'DEF']:
            selected_player = ('No Selection', pos, 0)
            player_selected = False
            for player in roster_with_scores:
                if player[1] == pos:
                    selected_player = player
                    player_selected = True
                    break
            lineup.append(selected_player)
            if player_selected:
                roster_with_scores.remove(selected_player)
                
        # fill flex
        selected_player = ('No Selection', pos, 0)
        for player in roster_with_scores:
            if player[1] in ['WR', 'RB', 'TE']:
                selected_player = player
                player_selected = True
                break
        lineup.append(selected_player)
        
        performance = np.sum(x[2] for x in lineup)
        
        fantasy_lineups.append(lineup)
        fantasy_team_performances.append(performance)
        
    return fantasy_team_performances, fantasy_lineups
  
def update_players(fantasy_players, fantasy_team_performances, num_players, mutation_rate=1.0, num_survivors = 4):
    '''
    Given a list of fantasy players with different strategies and the performance of each strategy,
    creates a new generation of fantasy players
    '''
    num_positions = 6 # number of positions
    
    performance_tuple_list = list (zip(fantasy_team_performances, fantasy_players))
    performance_tuple_list.sort(key = lambda x:x[0], reverse=True)
    
    playoff_players = np.array([x[1] for x in performance_tuple_list[:num_survivors]]) # get top players
    
    new_players = []
    # recombination
    for player in range(num_players):
        new_player = []
        parent1 = np.random.randint(playoff_players.shape[0])
        parent2 = np.random.randint(playoff_players.shape[0])
        for draft_round in range(fantasy_players.shape[1]):
            mean_chromosome = (playoff_players[parent1,draft_round,:] + playoff_players[parent2,draft_round,:])/2
            
            weights = mutation_rate * np.random.random(num_positions) # initialize random weights
            mutated_chromosome = mean_chromosome +  weights
            normed_chromosome = mutated_chromosome/np.sum(mutated_chromosome) # normalize so weights sum to 1
            
            new_player.append(normed_chromosome)

        new_players.append(new_player)
    
    return np.array(new_players)
     
