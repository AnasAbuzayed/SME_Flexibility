# -*- coding: utf-8 -*-
"""
© Anas Abuzayed 2023  <anas.abuzayed@hs-offenburg.de>
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import pypsa
import seaborn as sns
import yaml
from matplotlib import pyplot
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

ref=config['scenario']['ref']
net=config['scenario']['clusters']



data=pd.read_csv('../data/{}/{}_data.csv'.format(net,net),index_col=0)


scenarios_settings=pd.read_excel('../data/Scenarios.xlsx',sheet_name='Flex_hours', index_col=0)

SC_DSM={}
xls = pd.ExcelFile('../data/{}/{}_DSM_Usage_Infos.xlsx'.format(net, net))
for scenario in xls.sheet_names:
    df1 = pd.read_excel(xls, scenario,index_col=0)
    SC_DSM[scenario]=df1.copy()

SC_curtailment={}
xls_curtailment = pd.ExcelFile('../data/{}/{}_Curtailment_all.xlsx'.format(net, net))
for scenario in xls_curtailment.sheet_names:
    df1 = pd.read_excel(xls_curtailment, scenario,index_col=0)
    SC_curtailment[scenario]=df1.copy()

scenarios_settings.drop('S129',inplace=True)



for sc in scenarios_settings.index:
    scenarios_settings.loc[sc,'Energy']= SC_DSM[sc]['Energy'].sum()
    scenarios_settings.loc[sc,'Money']= SC_DSM[sc]['Money'].sum()
    scenarios_settings.loc[sc,'Utilization_before']=SC_DSM[sc].loc[2020:2044,'Utilization'].mean()
    scenarios_settings.loc[sc,'Utilization_after']=SC_DSM[sc].loc[2045:2050,'Utilization'].mean()
    



df_all=pd.DataFrame(0,index=scenarios_settings.index,columns=data.columns)

df_all[data.columns] = data[data.columns]
cmap = plt.get_cmap(name='jet', lut=None)




#%% Figure 4
df = pd.DataFrame({'Flex':scenarios_settings.Flex,
                   'Max_hours':scenarios_settings.Max_hours,
                   'Usage':df_all['Flexibility Average Usage'],
                   'Flex_cost':scenarios_settings.Flex_cost*1000})

table = pd.pivot_table(df, values='Usage', index=['Flex'],
                       columns=['Max_hours'], aggfunc="mean")
table=table.T
table.sort_index(ascending=False,inplace=True)


fig, ax = plt.subplots()
fig.set_size_inches(15,8)
sns.heatmap(table,linewidths=1, cmap='crest',
            cbar_kws={'label': 'SME Average Usage [%]',
                      "shrink":1,
                      'extend':'max', 
                      'extendfrac':0.1},
            robust=True,rasterized=True,square=True)
sns.set(font_scale=2)
ax.set_ylabel('Flexibility Duration in hours', fontsize=18)
ax.set_xlabel('Flexibility Potential in %', fontsize=18)
plt.title("Usage of different SME settings", fontsize=20)
fig.tight_layout()
plt.savefig('../Results/{}/SME Usage - Potential-Duration'.format(net),bbox_inches='tight',dpi=600)





table = pd.pivot_table(df, values='Usage', index=['Flex_cost'],
                       columns=['Max_hours'], aggfunc="mean")
table=table.T
table.sort_index(ascending=False,inplace=True)


fig, ax = plt.subplots()
fig.set_size_inches(15,8)
sns.heatmap(table,linewidths=1, cmap='crest',
            cbar_kws={'label': 'SME Average Usage [%]',
                      "shrink":1,
                      'extend':'max', 
                      'extendfrac':0.1},
            robust=True,rasterized=True,square=True)
sns.set(font_scale=2)
ax.set_ylabel('Flexibility Duration in hours', fontsize=18)
ax.set_xlabel('Flexibility Cost in Eur/MWh', fontsize=18)
plt.title("Usage of different SME settings", fontsize=20)
fig.tight_layout()
plt.savefig('../Results/{}/SME Usage - Cost-Duration'.format(net),bbox_inches='tight',dpi=600)










#%% Figure 6




df = pd.DataFrame({'Flex':scenarios_settings.Flex,
                   'Max_hours':scenarios_settings.Max_hours,
                   'Energy':scenarios_settings.Energy,
                   'Flex_cost':scenarios_settings.Flex_cost*1000})

table = pd.pivot_table(df, values='Energy', index=['Flex'],
                       columns=['Max_hours'], aggfunc="mean")
table=table.T
table.sort_index(ascending=False,inplace=True)

fig, ax = plt.subplots()
fig.set_size_inches(15,8)
sns.heatmap(table,linewidths=1, cmap='crest',
            cbar_kws={'label': 'SME Load Shifting in GWh',
                      "shrink":1,
                      'extend':'max', 
                      'extendfrac':0.1},
            robust=True,rasterized=True,square=True)
sns.set(font_scale=2)
ax.set_ylabel('Flexibility Duration in hours', fontsize=18)
ax.set_xlabel('Flexibility Potential in %', fontsize=18)
plt.title("Load Shifting from SME ", fontsize=20)
fig.tight_layout()
plt.savefig('../Results/{}/SME Energy- Potential-Duration'.format(net),bbox_inches='tight',dpi=600)




df = pd.DataFrame({'Flex':scenarios_settings.Flex,
                   'Max_hours':scenarios_settings.Max_hours,
                   'Energy':scenarios_settings.Energy,
                   'Flex_cost':scenarios_settings.Flex_cost*1000})

table = pd.pivot_table(df, values='Energy', index=['Flex_cost'],
                       columns=['Max_hours'], aggfunc="mean")
table=table.T
table.sort_index(ascending=False,inplace=True)

fig, ax = plt.subplots()
fig.set_size_inches(15,8)
sns.heatmap(table,linewidths=1, cmap='crest',
            cbar_kws={'label': 'SME Load Shifting in GWh',
                      "shrink":1,
                      'extend':'max', 
                      'extendfrac':0.1},
            robust=True,rasterized=True,square=True)
sns.set(font_scale=2)
ax.set_ylabel('Flexibility Duration in hours', fontsize=18)
ax.set_xlabel('Flexibility Cost in Eur/MWh', fontsize=18)
plt.title("Load Shifting from SME ", fontsize=20)
fig.tight_layout()
plt.savefig('../Results/{}/SME Energy - Cost-Duration'.format(net),bbox_inches='tight',dpi=600)




#%% Figure 7



df = pd.DataFrame({'Flex':scenarios_settings.Flex,
                   'Max_hours':scenarios_settings.Max_hours,
                   'Energy':scenarios_settings.Money/1e3, # kEUR
                   'Flex_cost':scenarios_settings.Flex_cost*1000})

table = pd.pivot_table(df, values='Energy', index=['Flex'],
                       columns=['Max_hours'], aggfunc="mean")
table=table.T
table.sort_index(ascending=False,inplace=True)

fig, ax = plt.subplots()
fig.set_size_inches(15,8)
sns.heatmap(table,linewidths=1, cmap='crest',
            cbar_kws={'label': 'Cost in Million Euros',
                      "shrink":1,
                      'extend':'max', 
                      'extendfrac':0.1},
            robust=True,rasterized=True,square=True)
sns.set(font_scale=2)
ax.set_ylabel('Flexibility Duration in hours', fontsize=18)
ax.set_xlabel('Flexibility Potential in [%]', fontsize=18)
plt.title("Total Cost of SME Flexibility", fontsize=20)
fig.tight_layout()
plt.savefig('../Results/{}/SME Cost- Potential-Duration'.format(net),bbox_inches='tight',dpi=600)





df = pd.DataFrame({'Flex':scenarios_settings.Flex,
                   'Max_hours':scenarios_settings.Max_hours,
                   'Energy':scenarios_settings.Money/1e3, # kEUR
                   'Flex_cost':scenarios_settings.Flex_cost*1000})

table = pd.pivot_table(df, values='Energy', index=['Flex_cost'],
                       columns=['Max_hours'], aggfunc="mean")
table=table.T
table.sort_index(ascending=False,inplace=True)

fig, ax = plt.subplots()
fig.set_size_inches(15,8)
sns.heatmap(table,linewidths=1, cmap='crest',
            cbar_kws={'label': 'Cost in Million Euros',
                      "shrink":1,
                      'extend':'max', 
                      'extendfrac':0.1},
            robust=True,rasterized=True,square=True)
sns.set(font_scale=2)
ax.set_ylabel('Flexibility Duration in hours', fontsize=18)
ax.set_xlabel('Flexibility Cost in Eur/MWh', fontsize=18)
plt.title("Total Cost of SME Flexibility", fontsize=20)
fig.tight_layout()
plt.savefig('../Results/{}/SME Cost- Cost-Duration'.format(net),bbox_inches='tight',dpi=600)


#%% Fig 14



df = pd.DataFrame({'Flex':df_all['Flexibility Potential'],
                   'Max_hours':df_all['Flexibility Duration'],
                   'Usage': df_all['DC 2045 Power']+df_all['AC 2045 Power']+
                   df_all['Biomass 2045 Power']+df_all['Battery 2045 Power']+
                   df_all['Hydrogen 2045 Power']+df_all['Load Shedding Peak'],
                   'Flex_cost':df_all['Flexibility Cost']})

n=pypsa.Network('../data/{}/{}/{}.nc'.format(net,ref,2045))
DC=n.links.p_nom.sum()
AC=n.lines.s_nom.sum()
bio=n.generators.p_nom_opt[n.generators.carrier=='biomass'].sum()
bat=n.storage_units.p_nom_opt[n.storage_units.carrier=='battery'].sum()
h2=n.storage_units.p_nom_opt[n.storage_units.carrier=='H2'].sum()
load=n.generators_t.p[n.generators.index[n.generators.carrier=='load']].sum(axis=1).max()

df.Usage-=(bio+bat+h2+load+DC+AC)




table = pd.pivot_table(df, values='Usage', index=['Flex'],
                       columns=['Flex_cost'], aggfunc="mean")
table=table.T
table.sort_index(ascending=False,inplace=True)

fig, ax = plt.subplots()
fig.set_size_inches(15,8)
sns.heatmap(table,linewidths=1, cmap='crest',
            cbar_kws={'label': 'Average Deviation [MW]',
                      "shrink":1,
                      'extend':'max', 
                      'extendfrac':0.1},
            robust=True,rasterized=True,square=True)
sns.set(font_scale=2)
ax.set_ylabel('SME Flexibility Costs in Euro/MWh', fontsize=18)
ax.set_xlabel('SME Flexibility Potential in %', fontsize=18)
plt.title("Flexibility Investments wrt REF scenario", fontsize=20)
fig.tight_layout()
plt.savefig('../Results/{}/SME Investments'.format(net),bbox_inches='tight',dpi=600)





#%%


xls = pd.ExcelFile('../data/{}/{}_CO2_Emissions.xlsx'.format(net, net))


df = pd.DataFrame({'Flex':scenarios_settings.Flex,
                   'Max_hours':scenarios_settings.Max_hours,
                   'Usage':df_all['CO2 Emissions']-pd.read_excel(xls, 'S129',index_col=0).sum().sum()/1e6,
                   'Flex_cost':scenarios_settings.Flex_cost*1000})


table = pd.pivot_table(df, values='Usage', index=['Flex_cost'],
                       columns=['Max_hours'], aggfunc="min")
table=table.T
table.sort_index(ascending=False,inplace=True)

fig, ax = plt.subplots()
fig.set_size_inches(15,8)
sns.heatmap(table,linewidths=1, cmap='crest',
            cbar_kws={'label': 'Abatement [Million tonnes]',
                      "shrink":1,
                      'extend':'max', 
                      'extendfrac':0.1},
            vmin=round(table.min().min()),vmax=0,
            robust=True,rasterized=True,square=True)
sns.set(font_scale=2)
ax.set_ylabel('SME Flexibility Duration in hours', fontsize=18)
ax.set_xlabel('SME Flexibility Cost in Eur/MWh', fontsize=18)
plt.title("Emissions Abatement wrt REF scenario", fontsize=20)
fig.tight_layout()
plt.savefig('../Results/{}/SME CO2- Cost-Duration'.format(net),bbox_inches='tight',dpi=600)




table = pd.pivot_table(df, values='Usage', index=['Flex'],
                       columns=['Max_hours'], aggfunc="min")
table=table.T
table.sort_index(ascending=False,inplace=True)

fig, ax = plt.subplots()
fig.set_size_inches(15,8)
sns.heatmap(table,linewidths=1, cmap='crest',
            cbar_kws={'label': 'Abatement [Million tonnes]',
                      "shrink":1,
                      'extend':'max', 
                      'extendfrac':0.1},
            vmin=round(table.min().min()),vmax=0,
            robust=True,rasterized=True,square=True)
sns.set(font_scale=2)
ax.set_ylabel('SME Flexibility Duration in hours', fontsize=18)
ax.set_xlabel('SME Flexibility Potential in %', fontsize=18)
plt.title("Emissions Abatement wrt REF scenario", fontsize=20)
fig.tight_layout()
plt.savefig('../Results/{}/SME CO2- Potential-Duration'.format(net),bbox_inches='tight',dpi=600)




#%% Fig 24


df = pd.DataFrame({'Flex':scenarios_settings.Flex,
                   'Max_hours':scenarios_settings.Max_hours,
                   'Usage':df_all['Total System Cost']/1e6,
                   'Flex_cost':scenarios_settings.Flex_cost*1000})

objective=pd.read_excel('../data/{}/{}/objective.xlsx'.format(net,ref), index_col=0)

df.Usage-=(objective.objective.sum()/1e6)


table = pd.pivot_table(df, values='Usage', index=['Flex_cost'],
                       columns=['Max_hours'], aggfunc="mean")
table=table.T
table.sort_index(ascending=False,inplace=True)


fig, ax = plt.subplots()
fig.set_size_inches(15,8)
sns.heatmap(table,linewidths=1, cmap='crest',
            cbar_kws={'label': 'Cost Savings in Billion Euros',
                      "shrink":1,
                      'extend':'max', 
                      'extendfrac':0.1},
            robust=True,rasterized=True,square=True)
sns.set(font_scale=2)
ax.set_ylabel('Flexibility Duration in hours', fontsize=18)
ax.set_xlabel('Flexibility Cost in Euro/MWh', fontsize=18)
plt.title("Total System Cost Savings wrt REF scenario", fontsize=20)
fig.tight_layout()
plt.savefig('../Results/{}/SME Total Cost- Cost-Duration'.format(net),bbox_inches='tight',dpi=600)




table = pd.pivot_table(df, values='Usage', index=['Flex'],
                       columns=['Max_hours'], aggfunc="mean")
table=table.T
table.sort_index(ascending=False,inplace=True)

fig, ax = plt.subplots()
fig.set_size_inches(15,8)
sns.heatmap(table,linewidths=1, cmap='crest',
            cbar_kws={'label': 'Cost Savings in Billion Euros',
                      "shrink":1,
                      'extend':'max', 
                      'extendfrac':0.1},
            robust=True,rasterized=True,square=True)
sns.set(font_scale=2)
ax.set_ylabel('Flexibility Duration in hours', fontsize=18)
ax.set_xlabel('SME Flexibility Potential in %', fontsize=18)
plt.title("Total System Cost Savings wrt REF scenario", fontsize=20)
fig.tight_layout()
plt.savefig('../Results/{}/SME Total Cost- Potential-Duration'.format(net),bbox_inches='tight',dpi=600)


table = pd.pivot_table(df, values='Usage', index=['Flex_cost'],
                       columns=['Flex'], aggfunc="mean")
table=table.T
table.sort_index(ascending=False,inplace=True)


fig, ax = plt.subplots()
fig.set_size_inches(7.35,8)
sns.heatmap(table,linewidths=1, cmap='crest',
            cbar_kws={'label': 'Cost Savings in Billion Euros',
                      "shrink":1,
                      'extend':'max', 
                      'extendfrac':0.1},
            robust=True,rasterized=True,square=False)
sns.set(font_scale=2)
ax.set_xlabel('Flexibility Cost in Euro/MWh', fontsize=18)
ax.set_ylabel('Flexibility Potential in %', fontsize=18)
plt.title("Total System Cost Savings wrt REF scenario", fontsize=20)
fig.tight_layout()
plt.savefig('../Results/{}/SME Total Cost- Cost-Potential'.format(net),bbox_inches='tight',dpi=600)



#%% FlexRequirements Fig 13



d_temp=data[['Flexibility Cost','Flexibility Duration','Flexibility Potential']]
d_temp['Flex'] = data['Hydrogen 2045 Energy'] + data['battery 2045 Energy'] + data['Biomass Utilization 2045'] 


n=pypsa.Network('../data/{}/{}/{}.nc'.format(net,ref,2045))
h2=n.storage_units_t.p_dispatch[n.storage_units.index[n.storage_units.carrier=='H2']].sum().sum()
b2=n.storage_units_t.p_dispatch[n.storage_units.index[n.storage_units.carrier=='battery']].sum().sum()
bio=n.generators_t.p[n.generators.index[n.generators.carrier=='biomass']].sum().sum()
d_temp['Flex']-=(h2+b2+bio)

d_temp['Flex']/=1e3


fig, ax = pyplot.subplots(figsize=(16,8))#,dpi=600)
sns.scatterplot(x='Flexibility Duration', y='Flex',
                data=d_temp, hue='Flexibility Potential',
                ax=ax,sizes=(20, 200),legend='full',s=100)
ax.collections[0].set_sizes([200])
plt.legend(markerscale=1.7,title='Flexibility Potential', title_fontsize=18,loc='best',fontsize=14)
plt.setp(plt.gca().get_legend().get_texts(), fontsize='18') #legend 'list' fontsize
ax.set_ylabel('Other Flexibility Utilization in GWh', fontsize=18)
ax.set_xlabel('Flexibility Duration in hours', fontsize=18)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.title("Flexibility Requirements wrt REF scenario", fontsize=20)
plt.savefig('../Results/{}/Flex Requirement wrt REF'.format(net),bbox_inches='tight',dpi=600)




#%% Flex Usage over years Fig 5
SC_DSM


scenarios=scenarios_settings.index
fig,ax = plt.subplots(1,1)
fig.set_size_inches(12,6)
for potential in scenarios_settings.loc[:,'Flex_cost'].unique():
    scs=list(set(data.index) & set(scenarios_settings.index[scenarios_settings.Flex_cost==potential]))
    temp=pd.DataFrame(0,index=range(2025,2051),columns=['Utilization'])
    for scenario in scs:
        temp['Utilization']+= SC_DSM[scenario]['Utilization']
    (temp/len(scs)).plot(legend=None, color=colors[str(potential)],ax=ax,linewidth=3)
plt.ylabel('DSM Average Utilization Rate [%]', fontsize=18)
plt.xlabel('Year', fontsize=18)
patch0 = mpatches.Patch(color=colors["0.1"], label='100 Euro/MWh')
patch1 = mpatches.Patch(color=colors["0.07"], label='70 Euro/MWh')
patch2 = mpatches.Patch(color=colors["0.05"], label='50 Euro/MWh')
patch3 = mpatches.Patch(color=colors["0.01"], label='10 Euro/MWh')
ax.legend(handles=[patch0,patch1,patch2,patch3], loc='best',
          fontsize=15,fancybox=True,frameon=True)
ax.set_facecolor('gainsboro')
plt.grid(alpha=0.7)
plt.xticks(size=15)
plt.yticks(size=15)
plt.savefig('../Results/{}/SME Usage over years'.format(net),bbox_inches='tight',dpi=600)



