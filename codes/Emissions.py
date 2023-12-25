# -*- coding: utf-8 -*-
"""
© Anas Abuzayed 2023  <anas.abuzayed@hs-offenburg.de>
"""


import pypsa
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import yaml
import datetime
import matplotlib.patches as mpatches

plt.style.use('seaborn')

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

with open(r'../config.yaml') as file:
    config= yaml.load(file, Loader=yaml.FullLoader)

createFolder('../'+config['scenario']['summary_dir']+'/'+str(config['scenario']['clusters']))

colors=config['plotting']['tech_colors']

S=config['scenario']['ref']
net=config['scenario']['clusters']

scenarios=[S]



gen=pd.read_csv('../data/{}/{}/Generation_Bar.csv'.format(net,'S129'),index_col=0)
carriers=['coal','lignite','CCGT','OCGT','oil']
co= pd.DataFrame(index =list(range(2025,2045)),columns=carriers)

for i,scenario in enumerate(scenarios):
    print(scenario)
    for year in co.index:
        n=pypsa.Network('../data/{}/{}/{}.nc'.format(net,S,year))
        for tech in co.columns:
            e = n.generators_t.p[n.generators.index[n.generators.carrier==tech]]
            effi = n.generators.efficiency[n.generators.carrier==tech]
            co2_factor=n.carriers[n.carriers.co2_emissions!=0].loc[tech,'co2_emissions']
            co.loc[year,tech] = (e/effi*co2_factor).sum().sum()





df=co.copy()/1e6
df.loc[2045]=0

df.drop((df.max()[df.max() < 1.]).index,axis=1,inplace=True)
gen=pd.read_csv('../data/{}/{}/Generation_Bar.csv'.format(net,'S129'),index_col=0)
gen=gen.loc[2025:2045,df.columns]


fig,ax = plt.subplots(1,1)
fig.set_size_inches(15,8)
plt.grid(alpha=0.7)
df.plot(kind='area',color=[colors[col] for col in df.columns],
        linewidth=0,ax=ax,alpha=0.4,legend=None)
plt.ylabel("CO2 Emissions [MtCO2]",fontsize=15)
plt.title('Total System Emissions',fontsize=30)
plt.yticks(np.arange(0, 126, step=25),rotation='vertical',fontsize=18)
plt.xticks(np.arange(2025, 2046, step=1),rotation='vertical',fontsize=18)
ax2 = ax.twinx()
ax2.set_ylabel("Energy [TWh]", fontsize=15)
plt.yticks(np.arange(0, 126, step=25),fontsize=18)
gen.loc[2025:2045,df.columns].plot(ax=ax2,color=[colors[col] for col in df.columns],
                                    linewidth=3,legend=None)
ax2.set_ylim(0,100)
lines, labels = ax.get_legend_handles_labels()
ax.legend(lines,labels,ncol=2, loc="center right",fontsize=15)
plt.tight_layout()
plt.savefig('../Results/{}/Scenarios Emissions.png'.format(net), dpi=600, bbox_inches='tight')



#%% All scenarios fossil fuel

scenarios_settings=pd.read_excel('../data/Scenarios.xlsx',sheet_name='Flex_hours', index_col=0)

year=2045
scenarios=scenarios_settings[scenarios_settings.Flex!=0].index
df_gas=pd.DataFrame(0,index=scenarios,columns=range(2025,2051))
df_bio=pd.DataFrame(0,index=scenarios,columns=range(2025,2051))
df_coal=pd.DataFrame(0,index=scenarios,columns=range(2025,2051))
gen129=pd.read_csv('../data/{}/{}/Generation_Bar.csv'.format(net,'S129'), index_col=0)


# for scenario in scenarios:
#     gen_bar=pd.read_csv('data/{}/{}/Generation_Bar.csv'.format(net,scenario), index_col=0)
#     df_coal.loc[scenario,:]=((gen_bar[['coal','lignite']]-gen129[['coal','lignite']]).loc[2025:]*1e3).sum(axis=1)
#     df_gas.loc[scenario,:]=((gen_bar[['CCGT','OCGT']]-gen129[['CCGT','OCGT']]).loc[2025:]*1e3).sum(axis=1)
#     df_bio.loc[scenario,:]=((gen_bar[['biomass']]-gen129[['biomass']]).loc[2025:]*1e3).sum(axis=1)
# df_gas.to_csv('data/{}/{}_Gas_all_scenarios.csv'.format(net,net))
# df_coal.to_csv('data/{}/{}_Coal_all_scenarios.csv'.format(net,net))
# df_bio.to_csv('data/{}/{}_Biomass_all_scenarios.csv'.format(net,net))


df_gas=pd.read_csv('../data/{}/{}_Gas_all_scenarios.csv'.format(net,net),index_col=0)
df_coal=pd.read_csv('../data/{}/{}_Coal_all_scenarios.csv'.format(net,net),index_col=0)
df_bio=pd.read_csv('../data/{}/{}_Biomass_all_scenarios.csv'.format(net,net),index_col=0)


at='Max_hours'
fig,ax = plt.subplots(3,1)
fig.set_size_inches(20,14)
for potential in scenarios_settings.loc[:,at].unique():
    scs=list(set(scenarios) & set(scenarios_settings.index[scenarios_settings[at]==potential]))
    df_coal.loc[scs,].mean(axis=0).plot(ax= ax[0], legend=None, color=colors[str(potential)],linestyle='solid')
    df_gas.loc[scs,].mean(axis=0).plot(ax= ax[1], legend=None, color=colors[str(potential)],linestyle='solid',sharex=ax[0])
    df_bio.loc[scs,].mean(axis=0).plot(ax= ax[2], legend=None, color=colors[str(potential)],linestyle='solid',sharex=ax[0])
fig.supylabel('Fossil Fuel Energy Reduction in GWh', fontsize=18)
patch0 = mpatches.Patch(color=colors["1"], label='1 Hour')
patch1 = mpatches.Patch(color=colors["2"], label='2 Hours')
patch2 = mpatches.Patch(color=colors["3"], label='3 Hours')
patch3 = mpatches.Patch(color=colors["4"], label='4 Hours')
patch4 = mpatches.Patch(color=colors["5"], label='5 Hours')
patch5 = mpatches.Patch(color=colors["6"], label='6 Hours')
patch6 = mpatches.Patch(color=colors["7"], label='7 Hours')
patch7 = mpatches.Patch(color=colors["8"], label='8 Hours')
ax[0].legend(handles=[patch0,patch1,patch2,patch3,patch4,patch5,patch6,patch7], loc='best',
          fontsize=15,fancybox=True,frameon=True,bbox_to_anchor=(1., 1.),
          title='Flexibility Duration',title_fontsize=14)
ax[0].set_facecolor('gainsboro')
ax[1].set_facecolor('gainsboro')
ax[2].set_facecolor('gainsboro')
ax[0].set_title('Coal Energy wrt reference scenario',fontsize=18)
ax[1].set_title('Gas Energy wrt reference scenario',fontsize=18)
ax[2].set_title('Biomass Energy wrt reference scenario',fontsize=18)
ax[0].grid(alpha=0.7)
ax[1].grid(alpha=0.7)
ax[2].grid(alpha=0.7)
plt.xticks(fontsize=18, rotation=90)
ax[0].yaxis.set_tick_params(labelsize=16)
ax[1].yaxis.set_tick_params(labelsize=16)
ax[2].yaxis.set_tick_params(labelsize=16)
plt.savefig('../Results/{}/Scenarios Fossil Fuel.png'.format(net), dpi=600, bbox_inches='tight')
