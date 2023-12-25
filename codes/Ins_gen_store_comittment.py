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




# Installation, Generation and Storage Bar Plots




def plot_clustered_stacked(dfall,title,y_label, H,labels=None, **kwargs):
    """Given a list of dataframes, with identical columns and index, create a clustered stacked bar plot. 
labels is a list of the names of the dataframe, used for the legend
title is a string for the title of the plot
H is the hatch used for identification of the different dataframe"""

    n_df = len(dfall)
    n_col = len(dfall[0].columns) 
    n_ind = len(dfall[0].index)
    axe = plt.subplot()

    for df in range(len(dfall)) : # for each data frame
        axe = dfall[df].plot(kind="bar",
                      linewidth=0,
                      stacked=True,
                      ax=axe,
                      edgecolor='k',
                      legend=False,
                      hatch=H[df],
                      grid=False,
                      color=[colors[col] for col in dfall[df].columns]
                      )  # make bar plots

    h,l = axe.get_legend_handles_labels() # get the handles we want to modify
    for i in range(0, n_df * n_col, n_col): # len(h) = n_col * n_df
        for j, pa in enumerate(h[i:i+n_col]):
            for rect in pa.patches: # for each index
                rect.set_x(rect.get_x() + 1 / float(n_df + 1) * i / float(n_col))
                # rect.set_hatch(H[int(i/11)]) #edited part     
                rect.set_width(1 / float(n_df + 1.5))
    
    axe.set_xticks((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.)
    axe.set_xticklabels(dfall[0].index, rotation = 0)
    # axe.set_title(title,fontsize=25)
    axe.grid(linestyle='-', linewidth='0.5', color='gray')
    axe.set_ylabel("{}".format(y_label),fontsize=25)
    axe.set_xlabel("Years",fontsize=25)
    axe.tick_params(axis='both', which='major', labelsize=25)


    # Add invisible data to add another legend

    n=[]        
    for i in range(n_df):
        n.append(axe.bar(0, 0, color="gray", hatch=H[i])) ## PROBLEM

    l1 = axe.legend(h[:n_col], l[:n_col], loc=[1.01, 0.5],shadow=True,fontsize=18)
    if labels is not None:
        l2 = plt.legend(n, labels, loc=[1.01, 0.1],shadow=True,fontsize=25) 
    axe.add_artist(l1)

    return axe

# create fake dataframes


years=[2025,2030,2035,2040,2045,2050]

ins1=pd.read_csv('../data/{}/{}/Installation_Bar.csv'.format(net,S),index_col=0)
gen1=pd.read_csv('../data/{}/{}/Generation_Bar.csv'.format(net,S),index_col=0)


techs=['coal','lignite','CCGT','OCGT',
       'biomass','ror',
       'offwind','onwind','solar']

ins1['offwind']=ins1['offwind-ac']+ins1['offwind-dc']
df1=ins1.loc[years,techs]


# Then, just call :
a=plot_clustered_stacked([df1],title='Technologies Installation',
                         y_label='Installed Power in GW',
                         H=[""])
plt.gcf().set_size_inches(15, 8)
plt.tight_layout()
plt.savefig('../Results/{}/Scenarios_installations.png'.format(net), dpi=600, bbox_inches='tight')
plt.show()



## Generation


gen1['offwind']=gen1['offwind-ac']+gen1['offwind-dc']

df1=gen1.loc[years,techs]

# Then, just call :
a=plot_clustered_stacked([df1],title='Energy Mix',
                         y_label='Energy in TWh',
                         H=[""])
plt.gcf().set_size_inches(15, 8)
plt.tight_layout()
plt.savefig('../Results/{}/Energy Mix.png'.format(net), dpi=600, bbox_inches='tight')
plt.show()




#### Storage


carriers=['PHS','hydro','battery','H2']
store=pd.read_csv('../data/{}/{}/Storage_Bar.csv'.format(net,S), usecols=carriers)

store.index=gen1.index

store=store/1000

techs=['battery','H2']


years=[2035,2040,2045,2050]
df1=store.loc[years,techs]

# Then, just call :
a=plot_clustered_stacked([df1],title='Storage Installation',
                         y_label='Installed Power in GW',
                         H=[""])
plt.gcf().set_size_inches(15, 8)
plt.tight_layout()
plt.savefig('../Results/{}/Storage installations.png'.format(net), dpi=600, bbox_inches='tight')
plt.show()



### Storage TWh


carriers=['battery','H2']
store=pd.read_csv('../data/{}/{}/Storage_Bar.csv'.format(net,S), usecols=carriers)

years=[2035,2040,2045,2050]

for year in years:
    n=pypsa.Network('../data/{}/{}/{}.nc'.format(net,S,year))
    for carrier in store.columns:
        store.loc[year,carrier] = n.storage_units_t.p_dispatch[n.storage_units.index[n.storage_units.carrier==carrier]].sum().sum() / 1e6
    
df1=store.loc[years]


# Then, just call :
a=plot_clustered_stacked([df1],title='Storage Capacity',
                         y_label='Storage Capacity in TWh',
                         H=[""])
plt.gcf().set_size_inches(15, 8)
plt.tight_layout()
plt.savefig('../Results/{}/Storage Capacity.png'.format(net), dpi=600, bbox_inches='tight')
plt.show()



##Storage Dispatch 
years=[2045,2050]
for year in years:
    n=pypsa.Network('../data/{}/{}/{}.nc'.format(net,S,year))
    
    
    n.storage_units_t.p_dispatch.index=periods=pd.date_range(periods=8760,freq='h',start=datetime.datetime(year, 1,1))
    
    
    fig,ax = plt.subplots(1,1)
    fig.set_size_inches(14,7)
    (n.storage_units_t.p_dispatch[n.storage_units.index[
        n.storage_units.carrier=='H2']].sum(axis=1)/1e3).plot(ax=ax,alpha=0.7,color='#ea048a',
                                                              label='H2')
    (n.storage_units_t.p_dispatch[n.storage_units.index[
        n.storage_units.carrier=='battery']].sum(axis=1)/1e3).plot(ax=ax,alpha=0.7,color='#b8ea04',
                                                                   label='Battery')
    plt.grid(alpha=0.7)
    ax.legend(loc='best',fontsize=16,fancybox=True, shadow=True)
    plt.title('Storage Dispatch - {} '.format(year),fontsize=18)
    plt.xlabel('Year',fontsize=18)
    plt.ylabel('Power [GWh]',fontsize=18)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    plt.savefig('../Results/{}/Storage Dispatch {} .png'.format(net,year), dpi=600, bbox_inches='tight')
    plt.show()

    
    storages=['PHS','hydro','H2','battery']
    
    
    
    p_by_carrier = n.generators_t.p.groupby(n.generators.carrier, axis=1).sum()
    e_by_carrier = n.storage_units_t.p.groupby(n.storage_units.carrier, axis=1).sum()
    load=pd.DataFrame({'Demand':n.loads_t.p_set.sum(axis=1)})
    load.index=p_by_carrier.index=e_by_carrier.index=periods
    
    p_by_carrier.rename(columns={"load": "Balance"},inplace=True)
    
    start=datetime.datetime(year, 1,1)
    end=datetime.datetime(year, 1,20)
    
    
    
    st_pt=pd.DataFrame()
    st_nt=pd.DataFrame()
    for store in storages:
        st_pt[store] = e_by_carrier[store].where(e_by_carrier[store]>0 , 0)
        st_nt[store] = e_by_carrier[store].where(e_by_carrier[store]<0 , 0)
    
    
    
    pos_total=pd.concat([p_by_carrier,st_pt],axis=1)
    

    
    n_t=st_nt[start:end]
    p_t=pos_total[start:end]
    p_t['offwind']=p_t['offwind-ac']+p_t['offwind-dc']
    p_t.drop(['offwind-ac', 'offwind-dc'], axis=1, inplace=True)
    
    columns=['coal','lignite','CCGT','OCGT','biomass','ror','offwind','onwind','solar','PHS','H2','battery','Balance']
    p_t=p_t[columns]
    
    n_t.drop((n_t.min()[n_t.min() > 10.]).index,axis=1,inplace=True)
    p_t.drop((p_t.max()[p_t.max() < 100.]).index,axis=1,inplace=True)
    y1= n_t.sum(axis=1).min()/1e3
    y2= p_t.sum(axis=1).max()/1e3
    delta=datetime.timedelta(hours=96)

    l=load[start:end]
    
    fig,ax = plt.subplots(1,1)
    fig.set_size_inches(20,10)
    (n_t/1e3)[start:end].plot(kind="area",ax=ax,linewidth=1,stacked=True,
                                    color=[colors[col] for col in n_t.columns])
    (p_t/1e3)[start:end].plot(kind="area",ax=ax,linewidth=1,stacked=True,
                                     color=[colors[col] for col in p_t.columns])
    (l/1e3).plot(kind="line",ax=ax,linewidth=2,color=['k'])
    lines, labels = ax.get_legend_handles_labels()
    ax.legend(lines[3:], [x.capitalize() for x in labels[3:]], ncol=3, loc="lower center",fontsize=16)
    ax.set_ylim([y1 - (25-abs(y1)%25), y2+25])
    ax.xaxis_date()
    ax.set_ylabel("GW",fontsize=18)
    ax.set_xlabel("Time",fontsize=18)
    plt.yticks(np.arange(y1 - (25-abs(y1)%25), y2 + (50-y2)%50, step=25),fontsize=16)
    plt.setp(ax.get_xticklabels(), rotation=45,fontsize=16)
    fig.tight_layout()
    plt.savefig('../Results/{}/Unit_Comit {}.png'.format(net,year), dpi=600, bbox_inches='tight')
    plt.show()
