#!/usr/bin/env python3
# From https://electowiki.org/wiki/Allocated_Score
# 2021-06-02T21:15:29-0600 

import pandas as pd
import numpy as np


def Allocated_Score(K, W, S):
    """
    Tabulate and return the list of winners, for an election with W winners and a
    score ranging from 0 to K. S is Pandas dataframe of scores on each ballot,
    with columns for candidates and rows for ballots.

    Illustrative example with 3 candidates, 2 winners, 10 ballots of each of 3 factions:
    >>> candidates = ['A', 'B', 'C']
    >>> scores = [[5, 4, 0]] * 10  +  [[4, 5, 0]] * 10  +  [[0, 2, 5]] * 10
    >>> S = pd.DataFrame.from_records(scores, columns=candidates)
    >>> Allocated_Score(5, 2, S)
    ['B', 'C']
    """

    #Normalize score matrix
    ballots = pd.DataFrame(S.values/K, columns=S.columns)
    
    #Find number of voters and quota size
    V = ballots.shape[0]
    quota = V/W
    ballot_weight = pd.Series(np.ones(V),name='weights')
    
    #Populate winners in a loop
    winner_list = []
    while len(winner_list) < W:

        weighted_scores = ballots.multiply(ballot_weight, axis="index")

        #Select winner
        w = weighted_scores.sum().idxmax()
    
        #Add winner to list
        winner_list.append(w)

        #remove winner from ballot
        ballots.drop(w, axis=1, inplace=True)
    
        #Create lists for manipulation
        cand_df = pd.concat([ballot_weight,weighted_scores[w]], axis=1).copy() 
        cand_df_sort = cand_df.sort_values(by=[w], ascending=False).copy()  
        
        #find the score where a quota is filled
        split_point = cand_df_sort[cand_df_sort['weights'].cumsum() < quota][w].min()
    
        #Amount of ballot for voters who voted more than the split point
        spent_above = cand_df[cand_df[w] > split_point]['weights'].sum()
        
        #Exhaust all ballots above split point
        if spent_above>0:    
            cand_df.loc[cand_df[w] > split_point, 'weights'] = 0.0
    
        #Amount of ballot for voters who gave a score on the split point
        weight_on_split = cand_df[cand_df[w] == split_point]['weights'].sum()

        #Fraction of ballot on split needed to be spent
        if weight_on_split>0:     
            spent_value = (quota - spent_above)/weight_on_split
    
            #Take the spent value from the voters on the threshold evenly
            cand_df.loc[cand_df[w] == split_point, 'weights'] = cand_df.loc[cand_df[w] == split_point, 'weights'] * (1 - spent_value)
    
        ballot_weight = cand_df['weights'].clip(0.0,1.0)

    return winner_list


def dup_factions(factions, num_winners):
    """Expand a list of factions by a factor of num_winners into a list of candidates

    >>> dup_factions(['A', 'B'], 3)
    ['A1', 'A2', 'A3', 'B1', 'B2', 'B3']
    """

    return [f'{f}{n}' for f in factions for n in range(1, num_winners+1)]


def dup_scores(scores, num_winners):
    """Expand a list of scores by a factor of num_winners, yielding one per candidate

    >>> dup_scores([0, 5], 3)
    [0, 0, 0, 5, 5, 5]
    """

    return [s for s in scores for n in range(num_winners)]


def tabulate_factions(max_score, num_winners, factions, candidates, profiles):
    """Tabulate and report election based on factions and voter profiles
    """

    print(f'Example election: {num_winners=}, {max_score=}, {factions=}')
    print('Profiles:')
    for profile, factor in profiles:
        print(f'  {factor}: {profile}')

    scores = []
    for profile, factor in profiles:
        scores.extend([dup_scores(profile, num_winners)] * factor)
    S = pd.DataFrame.from_records(scores, columns=candidates)

    print(f'Winners: {Allocated_Score(max_score, num_winners, S)}')


if __name__ == "__main__":
    # Run doctests
    import doctest
    doctest.testmod()
    
    # Sample election results, tabulation
    max_score = 5
    num_winners = 5

    # Study simplistic factions each with identitcal candidates
    factions = ['A', 'B', 'C']
    candidates = dup_factions(factions, num_winners)

    # Scores by faction for each of three voter profiles
    red   = [5, 0, 0]
    green = [0, 4, 5]
    blue  = [0, 3, 0]

    # profiles = [(red, 2), (green, 3)]
    profiles = [(red, 21), (green, 41), (blue, 38)]

    tabulate_factions(max_score, num_winners, factions, candidates, profiles)

    print()
    blue5  = [0, 5, 0]
    profiles5 = [(red, 21), (green, 41), (blue5, 38)]
    tabulate_factions(max_score, num_winners, factions, candidates, profiles5)

    # Election from star-core example at https://github.com/Equal-Vote/star-core
    candidates = 'Adam,Becky,Cindy,Dylan,Eliza'.split(',')

    scores = [
        [0,0,5,3,2],
        [4,0,3,3,2],
        [0,0,0,3,1],
        [2,0,0,3,4],
        [0,0,0,0,0],
        [1,5,0,3,5],
        [0,0,0,0,0],
    ]

    num_winners = 3

    print()

    print(f'star-core election: {candidates=}')
    print(f'{scores=}')
    for num_winners in range(1,6):
        S = pd.DataFrame.from_records(scores, columns=candidates)
        print(f' Result with {num_winners=}: {Allocated_Score(max_score, num_winners, S)}')
