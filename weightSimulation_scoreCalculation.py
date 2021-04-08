# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 08:44:17 2021
Criteria Weight Simulation based on OAT and UGS Suitability Calculation
"""

import pandas as pd
import numpy as np

def criteria_weight(input_act, range_percentage, step_size):
    ### retrieve the criteria names and importance scores from the dictionary as a list
    imp = []
    criteria = []
    for cri in input_act["criteria"].keys():
        imp.append(float(input_act["criteria"][cri]["cri_scores"]))
        criteria.append(cri[5:])
                
    ### calculate the default weights before the simulation
    #### n = number of criteria
    n = len(criteria)
    weights_0 = []
    for i in range(n):
        weights_0.append(np.float(imp[i]) / sum(imp))
    weights_0_df = pd.DataFrame(weights_0)
    
    ### initialize the criteria weight simulation (OAT)
    range_n = range(-range_percentage, range_percentage+1, step_size)
    ### create an empty dataframe based on the size of the range
    df_empty = np.empty(((len(range_n))*len(imp), len(imp)))
    df_empty[:] = np.nan
    df_empty = pd.DataFrame(df_empty, columns=criteria)
    ### start filling the empty dataframe with simulated criteria weights
    for i in range(len(imp)):
        for j in range(i*len(range_n), i*len(range_n)+len(range_n)):
            if i == 0:
                df_empty.iloc[i:len(range_n), i] = [(weights_0[i]+weights_0[i]*(j)/100) for j in range_n]   
            else:
                df_empty.iloc[i*len(range_n):i*len(range_n)+len(range_n), i] = [(weights_0[i]+weights_0[i]*(j)/100) for j in range_n]
                
    for i in range(len(imp)):
        for j in range(i*len(range_n), i*len(range_n)+len(range_n)):
            df_empty.iloc[j] = ((1-df_empty.iloc[i*len(range_n):i*len(range_n)+len(range_n), i])[j] * \
            weights_0_df/(1-weights_0[i]))[0].tolist()
            if i == 0:
                df_empty.iloc[i:len(range_n), i] = [(weights_0[i]+weights_0[i]*(j)/100) for j in range_n]
            else:
                df_empty.iloc[i*len(range_n):i*len(range_n)+len(range_n), i] = [(weights_0[i]+weights_0[i]*(j)/100) for j in range_n]

    ### check whether the sum of the criteria weights is 1.0!
    for i in range(len(df_empty)):
        if round(sum(df_empty.loc[i])) != 1:
            print("sum of the criteria weights is not equal to 1.0!")
            
    return df_empty


def main_activity(geometries, input_act, simulated_weights):

    criteria = []
    for cri in input_act["criteria"].keys():
        criteria.append(cri[5:])
    
    if input_act["act_name"] == "fris":
        ### select only the UGS that are larger than 50 m2
        green_spaces = geometries[(geometries['grwi'] > 50)]
        if input_act["city_name"] == "dd":
            ### filter out the following target types from related UGS
            green_spaces = green_spaces[(green_spaces['target_type'] != 'Plätze') & (geometries['target_type'] != 'Begrünte Stadtplätze') &\
                                        (green_spaces['target_type'] != 'cemetery') & (green_spaces['target_type'] != 'Friedhöfe') &\
                                        (green_spaces['target_type'] != 'Friedhof') & (green_spaces['target_type'] != 'Brachen (Wohnen, Industrie, Gewerbeflächen)') &\
                                        (green_spaces['target_type'] != 'allotments') & (green_spaces['target_type'] != 'Brachen (Ruderalflächen)') &\
                                        (green_spaces['target_type'] != 'nature_reserve')]
        else:
            green_spaces = green_spaces[(green_spaces['target_type'] != 'cemetery') & (green_spaces['target_type'] != 'Friedhöfe') &\
                                        (green_spaces['target_type'] != 'Friedhof') & (green_spaces['target_type'] != 'allotments') &\
                                        (green_spaces['target_type'] != 'brownfield') & (green_spaces['target_type'] != 'nature_reserve')]
        ### retrieve if any preference is defined as part of the meadow size...
        ### ...if not, then use raw min and max
        preference_grwi_min = input_act['criteria']["fris_grwi"]["sub_pre"]["min"]
        preference_grwi_max = input_act['criteria']["fris_grwi"]["sub_pre"]["max"]
        if preference_grwi_min == '':
            preference_grwi_min = green_spaces.query("grwi > 0.0").grwi.min()
        if preference_grwi_max == '':
            preference_grwi_max = green_spaces.grwi.max()
            
        limited_grwi = green_spaces.loc[(green_spaces.grwi >= float(preference_grwi_min)) & (green_spaces.grwi <= float(preference_grwi_max)), "grwi"]
        try: 
            second_smallest = max(sorted(green_spaces.loc[(green_spaces.grwi < float(preference_grwi_min)), "grwi"]))
            id_second_smallest = green_spaces.grwi.loc[green_spaces.grwi == second_smallest].index
            limited_grwi = limited_grwi.append(pd.Series(second_smallest, index = id_second_smallest))
        except:
            pass
        ind_limited = limited_grwi.index
        ### apply log transformation in order to implement Gaussian normalization function to meadow size 
        transformed_grwi = np.log(green_spaces.grwi.loc[ind_limited]+1)
        norm_grwi = np.exp(-np.power(transformed_grwi - np.mean(transformed_grwi), 2.) / (2 * np.power(np.std(transformed_grwi), 2)))
        norm_flwi = 1 - (green_spaces.flwi - green_spaces.flwi.min()) / (green_spaces.flwi.max() - green_spaces.flwi.min())
        transformed_scha = green_spaces.scha
        norm_scha = np.exp(-np.power(transformed_scha - np.mean(transformed_scha), 2.) / (2 * np.power(np.std(transformed_scha), 2)))
        transformed_baum = green_spaces.baum
        norm_baum = np.exp(-np.power(transformed_baum - np.mean(transformed_baum), 2.) / (2 * np.power(np.std(transformed_baum), 2)))            
        ### keep all scores in a list that are based on weight simulation and default weights
        scores_list = []
        for i in range(len(simulated_weights)):                    
            scores = norm_grwi*simulated_weights.loc[i][criteria.index('grwi')] + norm_flwi*simulated_weights.loc[i][criteria.index('flwi')] + \
            norm_scha*simulated_weights.loc[i][criteria.index('scha')] + norm_baum*simulated_weights.loc[i][criteria.index('baum')]
            scores = scores.dropna()
            scores_list.append(scores)
        
        return scores_list