# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 08:41:40 2021
Sensitivity Analysis
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import jenkspy
import matplotlib.pyplot as plt
plt.style.use('ggplot')
#import matplotlib.patches as mpatches
from matplotlib_scalebar.scalebar import ScaleBar
import contextily as ctx
### import functions for criteria weight simulation and suitability score calculation
from weightSimulation_scoreCalculation import criteria_weight, main_activity

### read data for playing Frisbee
data_fris = gpd.read_file("./data/data_frisbee.json")
# grwi: meadow size
# scha: shade
# baum: trees
# flwi: meadow flatness

#%% Criteria Weights Simulation based on OAT:
### create input dictionary for playing Frisbee incl. its corresponding criteria and their underlying importance scores (from 0 to 10)
input_act = {'act_name': "fris",
             'criteria': {'fris_grwi': {'cri_scores': '9.9', 'sub_pre': {'min': '', 'max': ''}},
                          'fris_scha': {'cri_scores': '6.4'},
                          'fris_baum': {'cri_scores': '5.7'},
                          'fris_flwi': {'cri_scores': '7.0'},
                         },
             'city_name': 'dd'
            }

### simulate criteria weights based on OAT: from 0 to 100% with 20% step size
criteria_weight_simulation = criteria_weight(input_act, 100, 20)

### save the simulated criteria weights (with 4 digits after comma) as a Latex table (.tex):
pd.options.display.float_format = '{:,.4f}'.format
with open('./criteria_weight_simulation_table.tex', 'w') as out:
    for i in range(len(criteria_weight_simulation.to_latex(index=False))):
        out.write(criteria_weight_simulation.to_latex(index=False)[i])

#%% Sensitivity Analysis:
### calculate suitability score list incl. scores for each UGS for playing Frisbee acc. to each simulated weight
scores_list = main_activity(data_fris, input_act, criteria_weight_simulation)
### due to several filtering methods (e.g. target type filter), not every UGS assigned with a score
### select only UGS that have a score
targetID_score = data_fris.loc[scores_list[0].index, "TARGET_ID"]
data_fris_score = data_fris[data_fris['TARGET_ID'].isin(targetID_score)]
### add all scores (44 different per UGS) into the data
for i in range(len(scores_list)):
    data_fris_score["scores_" + str(i)] = scores_list[i]

### since our number of run is 10 based on the simulation, every mid (scores_5, scores_16, etc.) score is actually the scores...
### ...that are calculated based on underlying weights (i.e. not simulated)
### take one of the non simulated scores and group it based on Natural breaks algorithm, create 2 groups
breaks = jenkspy.jenks_breaks(data_fris_score["scores_5"], nb_class=2)

### class 1: low
### keep the number of UGS in a list
default = 5
len(data_fris_score.query("scores_5 <= " + str(breaks[1])))
counts_1 = []
for i in range(len(criteria_weight_simulation)):
    counts_1.append(len(data_fris_score.query("scores_" + str(i) + " <= " + str(breaks[1]))))

### keep the percentage of changed UGS from original scored UGS in a list
changes_1 = []
for i in counts_1:
    changes_1.append(100*(len(data_fris_score.query("scores_" + str(default) + " <= " + str(breaks[1]))) - float(i)) / \
                     len(data_fris_score.query("scores_" + str(default) + " <= " + str(breaks[1]))))
changes_1 = np.abs(changes_1).tolist()

### class 2: high
### keep the number of UGS in a list
len(data_fris_score.query("scores_" + str(default) + " > " + str(breaks[1])))
counts_2 = []
for i in range(len(criteria_weight_simulation)):
    counts_2.append(len(data_fris_score.query("scores_" + str(i) + " > " + str(breaks[1]))))

### keep the percentage of changed UGS from original scored UGS in a list
changes_2 = []
for i in counts_2:
    changes_2.append(100*(len(data_fris_score.query("scores_" + str(default) + " > " + str(breaks[1]))) - float(i)) / \
                     len(data_fris_score.query("scores_" + str(default) + " > " + str(breaks[1]))))
changes_2 = np.abs(changes_2).tolist()

### calculate average score per UGS and form a table including avg scores, number of UGS changes and changes in percentages
avg_scores = [data_fris_score["scores_" + str(i)].mean() for i in range(0, 44)]
df_change_class = pd.DataFrame()
df_change_class["avg_scores"] = avg_scores
df_change_class["low_number"] = counts_1
df_change_class["high_number"] = counts_2
df_change_class["low_ratio"] = changes_1
df_change_class["high_ratio"] = changes_2

### save the simulated criteria weights (with 4 digits after comma) as a Latex table (.tex):
pd.options.display.float_format = '{:,.4f}'.format
with open('./sensitivity_UGS_scores.tex', 'w') as out:
    for i in range(len(df_change_class.to_latex(index=False))):
        out.write(df_change_class.to_latex(index=False)[i])

### calculate average change in percetanges per criteria
### drop the scores calculated based on default weights
df_change_class_w = df_change_class.drop([5, 16, 27, 38])

### create a dataframe keeps the average values
values = []
for i in range(0, 40, 10):
    values.append(df_change_class_w[i:i+10].mean()[["low_ratio", "high_ratio"]])
keys = ["grwi", "scha", "baum", "flwi"]

dict_avg = {}
j = 0
for i in keys:
    dict_avg[i] = values[j]
    j = j+1

df_avg_change = pd.DataFrame(data=dict_avg)
#print(df_avg_change)

#%% Plot Maps
### illustrate the effects of utmost weight simulations of criteria meadow flatness
### read polygon for drawing only the city border
city_border = gpd.read_file("./data/city_border.json")
### add classes to the data
data_fris_score["classes"] = np.nan
data_fris_score['classes'] = data_fris_score.query("scores_5 <= " + str(breaks[1]))['classes'].fillna("1")
data_fris_score['classes'].update(data_fris_score['classes'].fillna("2"))

### initialize plotting
### update coordinate systems to Pseudo-Mercator since base map comes with that:
df = data_fris_score.to_crs("EPSG:3857")
city_border = city_border.to_crs("EPSG:3857")

fig, (ax1, ax2, ax3) = plt.subplots(figsize=(20, 20), nrows=3)
### ax1
ax1.set_aspect('equal')
df.plot(ax=ax1, column='scores_33', cmap="Greens", legend=False, vmin=0.0, vmax=1.0)
### add a colorbar
fig = ax1.get_figure()
sm = plt.cm.ScalarMappable(cmap='Greens')
sm._A = []
cax = fig.add_axes([0.66, 0.13, 0.02, 0.75])
fig.colorbar(sm, cax=cax, orientation="vertical", label=r"UGS suitability scores for $playing \ Frisbee$", pad=0.02)

df.geometry.boundary.plot(color=None, edgecolor='#817d79', linewidth=0.07, ax=ax1)
city_border.geometry.boundary.plot(color=None, edgecolor='#1c7dbf', linewidth=1.25, ax=ax1)
ctx.add_basemap(ax1, source=ctx.providers.Stamen.TonerLite)
ax1.set_facecolor('#d6d6d6')
ax1.set_xticks([])
ax1.set_yticks([])
scalebar = ScaleBar(1, units="m", location="lower right", font_properties={'size':11})
x, y, arrow_length = 0.9385, 0.15, 0.059
ax1.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
             arrowprops=dict(facecolor='black', width=4, headwidth=12),
             ha='center', va='center', fontsize=11, xycoords=ax1.transAxes)
ax1.add_artist(scalebar)
### ax2
ax2.set_aspect('equal')
df.plot(ax=ax2, column='scores_38', cmap="Greens", legend=False, vmin=0.0, vmax=1.0)
### add a colorbar
fig = ax2.get_figure()
sm = plt.cm.ScalarMappable(cmap='Greens')
sm._A = []
cax = fig.add_axes([0.66, 0.13, 0.02, 0.75])
fig.colorbar(sm, cax=cax, orientation="vertical", label=r"UGS suitability scores for $playing \ Frisbee$", pad=0.02)

df.geometry.boundary.plot(color=None, edgecolor='#817d79', linewidth=0.07, ax=ax2)
city_border.geometry.boundary.plot(color=None, edgecolor='#1c7dbf', linewidth=1.25, ax=ax2)
ctx.add_basemap(ax2, source=ctx.providers.Stamen.TonerLite)
ax2.set_facecolor('#d6d6d6')
ax2.set_xticks([])
ax2.set_yticks([])
scalebar = ScaleBar(1, units="m", location="lower right", font_properties={'size':11})
x, y, arrow_length = 0.9385, 0.15, 0.059
ax2.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
             arrowprops=dict(facecolor='black', width=4, headwidth=12),
             ha='center', va='center', fontsize=11, xycoords=ax2.transAxes)
x, y, arrow_length = 0.5, 1.21, 0.21
ax2.annotate('', xy=(x, y), xytext=(x, y-arrow_length),
             arrowprops=dict(facecolor='black', width=8, headwidth=20),
             xycoords=ax2.transAxes)
plt.text(-7.10, 0.669, r"change the $meadow \ flatness$ weight by -100%",
         {'color': 'black', 'fontsize': 7, 'ha': 'left'}, wrap=True)
x, y, arrow_length = 0.5, -0.19, -0.1885
ax2.annotate('', xy=(x, y), xytext=(x, y-arrow_length),
             arrowprops=dict(facecolor='black', width=8, headwidth=20),
             xycoords=ax2.transAxes)
plt.text(-7.10, 0.318, r"change the $meadow \ flatness$ weight by +100%",
         {'color': 'black', 'fontsize': 7, 'ha': 'left'}, wrap=True)

ax2.add_artist(scalebar)
### ax3
ax3.set_aspect('equal')
df.plot(ax=ax3, column='scores_43', cmap="Greens", legend=False, vmin=0.0, vmax=1.0)
### add a colorbar
fig = ax3.get_figure()
sm = plt.cm.ScalarMappable(cmap='Greens')
sm._A = []
cax = fig.add_axes([0.66, 0.13, 0.02, 0.75])
fig.colorbar(sm, cax=cax, orientation="vertical", label=r"UGS suitability scores for $playing \ Frisbee$", pad=0.02)
df.geometry.boundary.plot(color=None, edgecolor='#817d79', linewidth=0.07, ax=ax3)
city_border.geometry.boundary.plot(color=None, edgecolor='#1c7dbf', linewidth=1.25, ax=ax3)
ctx.add_basemap(ax3, source=ctx.providers.Stamen.TonerLite)
ax3.set_xticks([])
ax3.set_yticks([])
ax3.set_facecolor('#d6d6d6')
scalebar = ScaleBar(1, units="m", location="lower right", font_properties={'size':11})
x, y, arrow_length = 0.9385, 0.15, 0.059
ax3.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
             arrowprops=dict(facecolor='black', width=4, headwidth=12),
             ha='center', va='center', fontsize=11, xycoords=ax3.transAxes)
ax3.add_artist(scalebar)
plt.subplots_adjust(wspace=0.1)
plt.savefig("./meadow_flatness_SA.png", dpi=200)
