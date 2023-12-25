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

scenario=config['scenario']['ref']
net=config['scenario']['clusters']


objective=pd.DataFrame(0,index=range(2025,2051),columns=['Total System Cost'])
addition=pd.read_excel('../data/{}/{}/addition.xlsx'.format(net,scenario), index_col=0)

objective['OPEX_ren']=0
objective['OPEX_conv']=0
objective['OPEX_flex']=0
objective['DSM']=0
objective['ac']=0
objective['dc']=0
objective['CAPEX_ren']=0
objective['CAPEX_conv']=0
objective['CAPEX_flex']=0

for idx in addition.index:
    addition.loc[idx,'carrier']=idx.split()[-1]

RES=['biomass','ror','offwind-ac','offwind-dc','onwind','solar']


for year in objective.index:
    n=pypsa.Network('../data/{}/{}/{}.nc'.format(net,scenario,year))

    # PP Generation cost
    for tech in n.generators.carrier[n.generators.carrier!='load'].unique():
        if tech in RES:            
            e_tot= n.generators_t.p[n.generators.index[n.generators.carrier==tech]]
            mar = n.generators.marginal_cost[(n.generators.carrier==tech)]            
            objective.loc[year,'OPEX_ren']+=(e_tot*mar).sum().sum()
        else:
            e_tot= n.generators_t.p[n.generators.index[n.generators.carrier==tech]]
            mar = n.generators.marginal_cost[(n.generators.carrier==tech)]
            objective.loc[year,'OPEX_conv']+=(e_tot*mar).sum().sum()

    # PP Investment cost
    for tech in addition.carrier.unique():
        if tech in RES:            
            p_nom=addition.p_nom[(addition.carrier==tech)&(addition.year_added==year)]
            cap=n.generators.capital_cost[(n.generators.carrier==tech)&(n.generators.p_nom_extendable==True)]            
            objective.loc[year,'CAPEX_ren']+=(p_nom*cap).sum()
        else:
            p_nom=addition.p_nom[(addition.carrier==tech)&(addition.year_added==year)]
            cap=n.generators.capital_cost[(n.generators.carrier==tech)&(n.generators.p_nom_extendable==True)]
            objective.loc[year,'CAPEX_conv']+=(p_nom*cap).sum()

    # Storage Investment cost
    for store_tech in n.storage_units.carrier[n.storage_units.p_nom_extendable==True].unique():
        p_nom=n.storage_units[(n.storage_units.carrier==store_tech)&(n.storage_units.p_nom_extendable==True)].p_nom_opt
        cap=n.storage_units.capital_cost[(n.storage_units.carrier==store_tech)
                                         &
                                         (n.storage_units.p_nom_extendable==True)]
        
        
        objective.loc[year,'CAPEX_flex']+=(p_nom*cap).sum()

    # Storage Dispatch cost
    for store_tech in n.storage_units.carrier.unique():
        e_dispatch=n.storage_units_t.p_dispatch[
            n.storage_units.index[
                n.storage_units.carrier==store_tech]]

        if store_tech=='DSM':
            mar= n.storage_units_t.marginal_cost[
                n.storage_units.index[n.storage_units.carrier==store_tech]
                ]
            objective.loc[year,'DSM']+=(e_dispatch*mar).sum().sum()
        else:            
            mar= n.storage_units.marginal_cost[
                    n.storage_units.carrier==store_tech]
    
            objective.loc[year,'OPEX_flex']+=(e_dispatch*mar).sum().sum()

    # Grid Expansion cost
    if year ==2020:
        objective.loc[year,'ac']=0
        objective.loc[year,'dc']=0
    else:
        nb=pypsa.Network('../data/{}/{}/{}.nc'.format(net,scenario,year-1))
        cap_ac=n.lines.loc[:,'s_nom'] - nb.lines.loc[:,'s_nom']
        mar_ac=n.lines.loc[:,'capital_cost']
        objective.loc[year,'ac']+=(cap_ac*mar_ac).sum()

    
        cap_dc=n.links.loc[:,'p_nom'] - nb.links.loc[:,'p_nom']
        mar_dc=n.links.loc[:,'capital_cost']        
        
        objective.loc[year,'dc']+=(cap_dc*mar_dc).sum()




objective['Total System Cost']=objective.sum(axis=1)

objective/=1e9







ob=objective[['OPEX_ren','OPEX_conv','CAPEX_conv','CAPEX_ren','CAPEX_flex']]
ob.columns=['Renewable Energy Cost', 'Conventional Energy Cost',
      'Conventional Investments Cost','Renewable Investments Cost',
      'Flexibility Investments Cost']

ob['Flexibility Investments Cost']+=objective['OPEX_flex']\
    +objective['DSM']+objective['ac']\
        +objective['dc']


ob.loc[2025:2051].plot.area(figsize=(20, 10),
             color=[colors[col] for col in ob.columns],alpha=0.7,
             linewidth=0)
plt.plot(objective['Total System Cost'].loc[2025:2051],'-k', label='Total Energy System Costs' ,linewidth=1)
plt.xlabel('Year', fontsize=20)
plt.ylabel('Costs in Billion Euro', fontsize=25)
plt.title('Total Annualized Energy System Costs',fontsize=30)
ax = plt.gca()
handles, labels = ax.get_legend_handles_labels()
labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0], reverse=True))
plt.style.use('default')
ax.legend(handles, labels,  prop={'size': 15},
          loc='best',fancybox=True, shadow=True,
          borderaxespad=2, framealpha=0.8,
          facecolor='gray')
ax.set_facecolor('gainsboro')
plt.grid()
plt.xticks(size=25)
plt.yticks(size=25)
plt.savefig('../Results/{}/Transition Costs.png'.format(net), dpi=600, bbox_inches='tight')
