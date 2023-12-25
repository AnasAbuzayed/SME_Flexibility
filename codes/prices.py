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

renewable_shares=pd.DataFrame(0,index=range(2025,2051),columns=['Renewables','Conventionals',
                                                                'Imbalance','Negative'])

temp= pd.DataFrame(0,index=range(2025,2051,1),columns=['Neg','Ren','Spot'])

for year in range(2025,2051):

    n=pypsa.Network('../data/{}/{}/{}.nc'.format(net,scenario,year))
    renewable_shares.loc[year,'Imbalance']=(n.generators_t.p[n.generators.index[n.generators.carrier=='load']].sum(axis=1) > n.loads_t.p.sum(axis=1)*0.01).sum()

    loads=n.loads_t.p_set.sum(axis=1).copy()
    load=n.loads_t.p_set.copy()

    fuel=0
    for conv_carrier in ['coal','lignite','CCGT','OCGT','oil']:
        fuel+=n.generators_t.p[n.generators.index[n.generators.carrier==conv_carrier]].sum().sum()
    renewable_shares.loc[year,'Conventionals']=(fuel/n.loads_t.p.sum().sum())*100

    r=0
    for carrier in ['solar','onwind','offwind-ac','offwind-dc']:
        for bus in n.generators.bus[n.generators.carrier==carrier].unique():
            cols=n.generators.index[(n.generators.carrier==carrier)&(n.generators.bus==bus)]
            
            g_pu= n.generators_t.p_max_pu[cols].mean(axis=1)
            p_nom= n.generators.p_nom[(n.generators.carrier==carrier)&
                                      (n.generators.bus==bus)].sum()
                        
            load[bus]-=g_pu*p_nom
        
        r+=n.generators_t.p[n.generators.index[n.generators.carrier==carrier]].sum().sum()
        loads-=(n.generators_t.p_max_pu[n.generators.index[n.generators.carrier==carrier]]
               *n.generators.p_nom[n.generators.carrier==carrier]).sum(axis=1)
 

    renewable_shares.loc[year,'Renewables']=(r/n.loads_t.p.sum().sum())*100
    if renewable_shares.loc[year,'Renewables']>100:
        renewable_shares.loc[year,'Renewables']=100
    
    renewable_shares.loc[year,'Negative']= loads.lt(0).sum()

    
    temp.loc[year,'Ren']=(r/n.loads_t.p.sum().sum())*100
    temp.loc[year,'Neg']=load.sum(axis=1).lt(0).sum()
    
    n.generators.loc[n.generators.carrier=='load','marginal_cost']=250
        
    merit=pd.DataFrame(100,n.buses_t.marginal_price.index, n.loads_t.p.columns)
    
    for bus in merit.columns:
        merit.loc[:,bus][load.loc[:,bus]<n.loads_t.p_set.loc[:,bus]*0.01]=0 # anything less than 1% of the actual demand ==> safety factor
        
        costs=(n.generators_t.p[n.generators.index[n.generators.bus==bus]] > 1)
        for col in costs.columns:
            costs[col] = costs[col].replace({True:n.generators.loc[col,'marginal_cost'],
                                     False:0})
            hours=merit.index[merit[bus]>0]
            merit.loc[hours,bus] = costs.loc[hours].max(axis=1)
                
        temp.loc[year,'Spot']=merit.mean().mean()








renewable_shares.columns=['Renewables Share [left axis]', 'Conventionals Share [left axis]',
                          'Hours with Imbalance [right axis]','Hours with negative or zero price [right axis]']



fig,ax = plt.subplots(1,1)
fig.set_size_inches(14,7)
renewable_shares.loc[:,'Renewables Share [left axis]'].plot(ax=ax,color='green')
renewable_shares.loc[:,'Conventionals Share [left axis]'].plot(ax=ax,color='brown')
plt.yticks(fontsize=18)
plt.xticks(fontsize=18)
plt.grid(alpha=0.7)
ax2 = ax.twinx()
renewable_shares.loc[:,'Hours with negative or zero price [right axis]'].plot(ax=ax2,color='red')
renewable_shares.loc[:,'Hours with Imbalance [right axis]'].plot(ax=ax2,color='black')
lines, labels = ax.get_legend_handles_labels()
lines.extend(ax2.get_legend_handles_labels()[0])
labels.extend(ax2.get_legend_handles_labels()[1])
ax.legend(lines,labels,ncol=1, loc="upper left",fontsize=18)
plt.setp(ax.get_xticklabels(), rotation=45)
ax.set_ylabel("Share of Total Demand [%]", fontsize=18)
ax2.set_ylabel("Hours", fontsize=18)
plt.xlabel('Year',fontsize=18)
plt.tight_layout()
plt.yticks(fontsize=18)
plt.savefig('../Results/{}/Negative Load.png'.format(net), dpi=600, bbox_inches='tight')










fig,ax = plt.subplots(1,1)
fig.set_size_inches(16,8)
temp.Spot.plot(ax=ax)
plt.grid(alpha=0.7)
plt.legend([])
plt.title('Average Wholesale Electricity Price',fontsize=20)
ax.set_ylabel("Price [Euro/MWh]",fontsize=20)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.tight_layout()
plt.savefig('../Results/{}/Wholesale Price.png'.format(net), dpi=600, bbox_inches='tight')

