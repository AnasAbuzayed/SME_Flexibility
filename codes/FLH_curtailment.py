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

S=config['scenario']['ref']
net=config['scenario']['clusters']




#%% Data preparation

if os.path.exists('../data/{}/{}_grid.csv'.format(net,net)) == False:
    grid=pd.DataFrame(0,index=range(2020,2051),columns=['AC','DC'])
    for year in range(2020,2051):
        n=pypsa.Network('../data/{}/{}/{}.nc'.format(net,S,year))
        grid.loc[year,'AC']=n.lines.s_nom.sum()
        grid.loc[year,'DC']=n.links.p_nom.sum()
    grid.to_csv('../data/{}/{}_grid.csv'.format(net,net))

elif os.path.exists('../data/{}/{}_FLH.csv'.format(net,net)) == False:
    
    res=['solar','onwind','offwind-ac','offwind-dc','biomass','ror']
    ins1=pd.read_csv('../data/{}/{}/Installation_Bar.csv'.format(net,S),index_col=0)
    gen1=pd.read_csv('../data/{}/{}/Generation_Bar.csv'.format(net,S),index_col=0)
    
    FLH=pd.DataFrame(0,index=range(2020,2051),columns=gen1.columns)
    
    for year in range(2020,2051):
        n=pypsa.Network('../data/{}/{}/{}.nc'.format(net,S,year))
        grid.loc[year,'AC']=n.lines.s_nom.sum()
        grid.loc[year,'DC']=n.links.p_nom.sum()
        for carrier in res:
            g=n.generators_t.p[n.generators.index[n.generators.carrier==carrier]].sum().sum()
            i=n.generators[n.generators.carrier==carrier].p_nom.sum()
            FLH.loc[year,carrier]= g/i
        if year in range(2020,2045):
            if year > 2020:
                nb=pypsa.Network('../data/{}/{}/{}.nc'.format(net,S,year-1))
                for carrier in ['coal','lignite']:
                    g=n.generators_t.p[n.generators.index[n.generators.carrier==carrier]].sum().sum()
                    i=nb.generators[n.generators.carrier==carrier].p_nom.sum()
                    FLH.loc[year,carrier]= g/i
                for carrier in ['CCGT','OCGT','oil']:
                    g=n.generators_t.p[n.generators.index[n.generators.carrier==carrier]].sum().sum()
                    i=nb.generators[n.generators.carrier==carrier].p_nom.sum()
                    FLH.loc[year,carrier]= g/i
    
            else:
                for carrier in ['coal','lignite']:
                    g=n.generators_t.p[n.generators.index[n.generators.carrier==carrier]].sum().sum()
                    i=ins1.loc[year,carrier]*1000#n.generators[n.generators.carrier==carrier].p_nom.sum()
                    if g/i > 8760 :
                        FLH.loc[year,carrier]= 8760
                    else:
                        FLH.loc[year,carrier]= g/i
    
                for carrier in ['CCGT','OCGT','oil']:
                    g=n.generators_t.p[n.generators.index[n.generators.carrier==carrier]].sum().sum()
                    i=ins1.loc[year,carrier]*1000#n.generators[n.generators.carrier==carrier].p_nom.sum()
                    if g/i > 8760 :
                        FLH.loc[year,carrier]= 8760
                    else:
                        FLH.loc[year,carrier]= g/i


    FLH.to_csv('../data/{}/FLH.csv'.format(net))




elif (os.path.exists('../data/{}/{}_Curtailment.csv'.format(net,net)) == False)&(os.path.exists('../data/{}/{}_Storage_Energy.csv'.format(net,net)) == False):

    curt=pd.DataFrame(0,index=range(2020,2051), columns=['solar','onwind','offwind-ac','offwind-dc'])
    store=pd.DataFrame(0,index=range(2020,2051), columns=['H2','battery'])
    for year in range(2020,2051):
        n=pypsa.Network('../data/{}/{}/{}.nc'.format(net,S,year))
        for tech in curt.columns:
            for bus in n.buses.index:
                p=n.generators.p_nom[(n.generators.carrier==tech)
                                     &
                                     (n.generators.bus==bus)].sum()
                pdis=n.generators_t.p[n.generators.index[(n.generators.carrier==tech)
                                     &
                                     (n.generators.bus==bus)]].sum(axis=1)
                
                pmax=p*n.generators_t.p_max_pu[n.generators.index[(n.generators.carrier==tech)
                                     &
                                     (n.generators.bus==bus)]].mean(axis=1)
                c=pmax.sum() - pdis.sum()
                if c > 0:
                    curt.loc[year,tech]+= c
    
        for carrier in store.columns:
            e=n.storage_units_t.p_dispatch[n.storage_units.index[n.storage_units.carrier==carrier]].sum().sum() 
            p=n.storage_units.p_nom[n.storage_units.carrier==carrier].sum()
            eff_store= n.storage_units.efficiency_store[n.storage_units.carrier==carrier].max()
            eff_dispatch= n.storage_units.efficiency_dispatch[n.storage_units.carrier==carrier].max()
            store.loc[year,carrier] = e / 1e6


    curt.to_csv('../data/{}/{}_Curtailment.csv'.format(net,net))
    store.to_csv('../data/{}/{}_Storage_Energy.csv'.format(net,net))

#%% Plots

FLH = pd.read_csv('../data/{}/{}_FLH.csv'.format(net,net),index_col=0)
grid = pd.read_csv('../data/{}/{}_grid.csv'.format(net,net),index_col=0)
curt = pd.read_csv('../data/{}/{}_Curtailment.csv'.format(net,net),index_col=0)
store = pd.read_csv('../data/{}/{}_Storage_Energy.csv'.format(net,net),index_col=0)




carriers=['battery','H2']

store=pd.read_csv('../data/{}/{}/Storage_Bar.csv'.format(net,S), usecols=carriers)
ins1=pd.read_csv('../data/{}/{}/Installation_Bar.csv'.format(net,S),index_col=0)

years=range(2025,2051)
store.index=range(2020,2051)

res=['solar','onwind','offwind']

flex=pd.DataFrame()
flex[['H2','battery']]=store[['H2','battery']]/1000
flex[['AC','DC']]=grid[['AC','DC']]/1000
flex['Grid']=(grid['AC']+grid['DC'])/1000
flex['Storage Flexibility']=store[['H2','battery']].sum(axis=1)/1000
flex['Grid Expansion']=grid.sum(axis=1)/1000

ins1['offwind']=ins1['offwind-ac']+ins1['offwind-dc']


fig,ax = plt.subplots(1,1)
fig.set_size_inches(14,7)
ins1.loc[years,res].plot(kind="line",ax=ax,linewidth=3,
                                color=[colors[col] for col in ins1[res].columns])
flex.loc[years,'Storage Flexibility'].plot(kind="line",ax=ax,linewidth=3,
                                color='pink')
flex.loc[years,'Grid'].plot(kind="line",ax=ax,linewidth=3,
                                color='red')
plt.grid(alpha=0.7)
plt.legend(loc='best',fontsize=16)
plt.title('Cumulative Installed Power',fontsize=18)
plt.xlabel('Year',fontsize=18)
plt.ylabel('Power [GW]',fontsize=18)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.tight_layout()
plt.savefig('../Results/{}/Cumulative Installed Power.png'.format(net), dpi=600, bbox_inches='tight')


FLH.replace(np.nan,0,inplace=True)
FLH.drop((FLH.max()[FLH.max() < 10.]).index,axis=1,inplace=True)

fig,ax = plt.subplots(1,1)
fig.set_size_inches(16,8)
FLH.loc[years,:].plot(kind="line",ax=ax,linewidth=3,
                                color=[colors[col] for col in FLH.columns])
plt.grid(alpha=0.7)
plt.legend(loc='best',fontsize=18)
plt.title('Technologies Full Load Hours',fontsize=18)
plt.xlabel('Year',fontsize=18)
plt.ylabel('Hours',fontsize=18)
plt.yticks([500,1000,1500,2000,2500,3000,4000,5000,6000,7000,8000],fontsize=18)
plt.tight_layout()
plt.xticks(fontsize=18)
plt.savefig('../Results/{}/FLH.png'.format(net), dpi=600, bbox_inches='tight')





curt=curt/1e6
curt['offwind']=curt['offwind-dc']+curt['offwind-ac']
curt=curt[['solar','onwind','offwind']]

curt=curt.loc[2025:]
store=store.loc[2030:]

# Plot
lns1=curt.plot(color=[colors[col] for col in curt.columns],linewidth=3)
plt.ylabel('Curtailment in TWh', fontsize=20)
plt.xlabel('Year', fontsize=20)
plt.gcf().set_size_inches(15, 8)
ax = plt.gca()
plt.grid()
ax2 = ax.twinx()
lns2=(store[['H2','battery']]/1e3).plot(ax=ax2,legend=None,linewidth=3,
                                          color=[colors[col] for 
                                                col in store[['H2','battery']].columns])
ax2.set_ylabel("Storage Flexibility [TWh]", fontsize=20)
lines, labels = ax.get_legend_handles_labels()
lines.extend(ax2.get_legend_handles_labels()[0])
labels.extend(ax2.get_legend_handles_labels()[1])
ax.legend(lines,labels,ncol=3, loc="best",fontsize=15)
plt.setp(ax.get_xticklabels(), rotation=45)
ax.xaxis.set_tick_params(labelsize=20)
ax.yaxis.set_tick_params(labelsize=20)
ax2.yaxis.set_tick_params(labelsize=20)
fig.tight_layout()
plt.savefig('../Results/{}/Total Curtailment'.format(net),bbox_inches='tight',dpi=600)


