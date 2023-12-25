# -*- coding: utf-8 -*-
"""
© Anas Abuzayed 2023  <anas.abuzayed@hs-offenburg.de>
"""



import os 
import yaml
import pypsa
import matplotlib.pyplot as plt
import pandas as pd
plt.style.use('seaborn')
from matplotlib import pyplot
import seaborn as sns

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





data=pd.read_csv('../data/{}/{}_data.csv'.format(net,net),index_col=0)


d_temp=data[['Flexibility Cost','Flexibility Duration','Flexibility Potential']]
d_temp['Flex'] = data['Hydrogen 2045 Energy'] + data['battery 2045 Energy'] + data['Biomass Utilization 2045'] 

n=pypsa.Network('../data/{}/{}/2045.nc'.format(net,S))

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
plt.savefig('../Results/{}/Flex_requirement_wrt_REF.png'.format(net), dpi=600, bbox_inches='tight')
