# -*- coding: utf-8 -*-
"""
© Anas Abuzayed 2023  <anas.abuzayed@hs-offenburg.de>
"""
#%% Preparation

from sklearn import preprocessing
import pandas as pd 
import os 
import pypsa
import matplotlib.pyplot as plt
import numpy as np
import os 
from math import pi
import yaml

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




plt.style.use('seaborn')


#%% Data Processing
if os.path.exists('../data/{}/{}_all_rose_data.csv'.format(net,net)):
    df_rose=pd.read_csv('../data/{}/{}_all_rose_data.csv'.format(net,net),index_col=0)
else:        
    
    xls_DSM = pd.ExcelFile('../data/{}/{}_DSM_Usage_Infos.xlsx'.format(net, net))
    xls_load = pd.ExcelFile('../data/{}/{}_Load_factor.xlsx'.format(net,net))
    xls_curtailment = pd.ExcelFile('../data/{}/{}_Curtailment_all.xlsx'.format(net,net))
    xls_spot = pd.ExcelFile('../data/{}/{}_Spot_Scs_Comparison.xlsx'.format(net,net))
    
    scenarios_settings=pd.read_excel('../data/Scenarios.xlsx',sheet_name='Flex_hours', index_col=0)
    scenarios_settings.drop('S129',inplace=True)
    
    n=pypsa.Network('../data/{}/{}/{}.nc'.format(net,S,2045))
    co2= pd.read_excel(pd.ExcelFile('../data/{}/{}_CO2_Emissions.xlsx'.format(net,net)), S,index_col=0)
    
    ins_bar=pd.read_csv('../data/{}/{}/Installation_Bar.csv'.format(net,S),index_col=0)
    gen_bar=pd.read_csv('../data/{}/{}/Generation_Bar.csv'.format(net,S),index_col=0)
    store_bar=pd.read_csv('../data/{}/{}/Storage_Bar.csv'.format(net,S),index_col=0)
    objective=pd.read_excel('../data/{}/{}/objective.xlsx'.format(net,S), index_col=0)
    shedding=pd.read_csv('../data/{}/{}_Imbalance.csv'.format(net,net), index_col=0)
    
    
    data=pd.read_csv('../data/{}/{}_data.csv'.format(net,net), index_col=0)
    df_all=pd.DataFrame(0,index=scenarios_settings.index,columns=data.columns)
    
    df_all[data.columns] = data[data.columns]
    
    
    df_rose=pd.DataFrame(index=scenarios_settings.index)
    
    df_rose['Total System Cost'] = data['Total System Cost']
    df_rose['CO2 Emissions'] = data['CO2 Emissions'] 
    df_rose['Grid Development'] = data['DC 2045 Power']+data['AC 2045 Power']
    
    
    df_rose['Biomass Power'] = data['Biomass 2045 Power'] 
    df_rose['Battery Power'] = data['Battery 2045 Power'] 
    df_rose['Hydrogen Power'] = data['Hydrogen 2045 Power']
    df_rose['Imbalance Power'] = data['Load Shedding Peak']
    
    df_rose['Flexibility Usage'] = data['Hydrogen 2045 Energy'] + data['battery 2045 Energy'] + data['Biomass Utilization 2045'] 
    df_rose['Hydrogen 2045 Energy'] = data['Hydrogen 2045 Energy'] 
    df_rose['battery 2045 Energy'] = data['battery 2045 Energy'] 
    df_rose['Biomass Utilization 2045'] = data['Biomass Utilization 2045'] 
    
    df_rose['Renewables Investments'] = data['Solar Actual Installations'] + data['Onwind Actual Installations']+data['Offwind Actual Installations']
    
    
    
    for sc in df_rose.index:    
        df_rose.loc[sc,'Peak Reduction']=(pd.read_excel(xls_load, sc,index_col=0)['Peak reduction']).mean()
        df_rose.loc[sc,'RES Curtailment']=pd.read_excel(xls_curtailment, sc,index_col=0).sum().sum()
    
        df_rose.loc[sc,'Spot Market']=(pd.read_excel(xls_spot, sc,index_col=0)['Spot']).mean()
        df_rose.loc[sc,'Grid Loading']=data.loc[sc,'AC Grid Loading']
        
        df_rose.loc[sc,'Total Imbalance']=shedding[sc].sum()
        df_rose.loc[sc,'Imbalance Peak']= data.loc[sc,'Load Shedding Peak']/1e3
    
        df_rose.loc[sc,'Total System Cost']=df_rose.loc[sc,'Total System Cost']
        df_rose.loc[sc,'CO2 Emissions']=df_rose.loc[sc,'CO2 Emissions']
        df_rose.loc[sc,'Grid Development']=df_rose.loc[sc,'Grid Development']
        df_rose.loc[sc,'Biomass Power']=df_rose.loc[sc,'Biomass Power']
        df_rose.loc[sc,'Battery Power']=df_rose.loc[sc,'Battery Power']
        df_rose.loc[sc,'Hydrogen Power']=df_rose.loc[sc,'Hydrogen Power']
        df_rose.loc[sc,'Imbalance Power']=df_rose.loc[sc,'Imbalance Power']
        df_rose.loc[sc,'Flexibility Usage']= df_rose.loc[sc,'Flexibility Usage']
        
        df_rose.loc[sc,'Renewables Investments']= df_rose.loc[sc,'Renewables Investments']
        
        df_rose.loc[sc,'battery 2045 Energy']= df_rose.loc[sc,'battery 2045 Energy']
        df_rose.loc[sc,'Hydrogen 2045 Energy']= df_rose.loc[sc,'Hydrogen 2045 Energy']
        df_rose.loc[sc,'Biomass Utilization 2045']= df_rose.loc[sc,'Biomass Utilization 2045']
    
        df_rose.loc[sc,'Biomass Utilization']= pd.read_csv('../data/{}/{}/Generation_Bar.csv'.format(net,sc),index_col=0).biomass.sum()
        df_rose.loc[sc,'Fossil Fuel Utilization']= pd.read_csv('../data/{}/{}/Generation_Bar.csv'.format(net,sc),index_col=0)[['CCGT','OCGT','oil','coal','lignite']].sum().sum()
        df_rose.loc[sc,'SME Usage']=(pd.read_excel(xls_DSM, sc,index_col=0)['Energy']).sum()/-1000 # negative for plotting purposes
        df_rose.loc[sc,'SME Money']= (pd.read_excel(xls_DSM, sc,index_col=0)['Money']).sum()/-1000 # negative for plotting purposes
    
    
    
    
    
    sc=S
    so=(ins_bar.loc[2050,'solar']-ins_bar.loc[2020,'solar'])
    onw=ins_bar.loc[2050,'onwind']-ins_bar.loc[2020,'onwind']
    ofw= (ins_bar.loc[2050,'offwind-ac']+ins_bar.loc[2050,'offwind-dc']-ins_bar.loc[2020,'offwind-ac']-ins_bar.loc[2020,'offwind-dc'])
    
    load_shedding=shedding[S].sum()
    load_shedding_peak=n.generators_t.p[n.generators.index[n.generators.carrier=='load']].sum(axis=1).max() # GW
    
    h2=n.storage_units_t.p_dispatch[n.storage_units.index[n.storage_units.carrier=='H2']].sum().sum()
    b2=n.storage_units_t.p_dispatch[n.storage_units.index[n.storage_units.carrier=='battery']].sum().sum()
    bio=n.generators_t.p[n.generators.index[n.generators.carrier=='biomass']].sum().sum()
    
    
    
    df_rose.loc[sc,'Peak Reduction'] = (pd.read_excel(xls_load, sc,index_col=0)['Peak reduction']).mean()
    df_rose.loc[sc,'RES Curtailment']=pd.read_excel(xls_curtailment, sc,index_col=0).sum().sum()
    
    df_rose.loc[sc,'Spot Market']=(pd.read_excel(xls_spot, sc,index_col=0)['Spot']).mean()
    
    df_rose.loc[sc,'Imbalance Peak']=load_shedding_peak/1e3
    df_rose.loc[sc,'Total Imbalance']=load_shedding
    
    df_rose.loc[sc,'Total System Cost']=objective.objective.sum()
    df_rose.loc[sc,'CO2 Emissions']=co2.sum().sum()/1e6
    df_rose.loc[sc,'Grid Development']=(n.links.p_nom.sum() + n.lines.s_nom.sum())
    df_rose.loc[sc,'Biomass Power']=n.generators.p_nom_opt[n.generators.carrier=='biomass'].sum()
    
    df_rose.loc[sc,'Battery Power']=n.storage_units.p_nom_opt[n.storage_units.carrier=='battery'].sum()
    df_rose.loc[sc,'Hydrogen Power']=n.storage_units.p_nom_opt[n.storage_units.carrier=='H2'].sum()
    df_rose.loc[sc,'Imbalance Power']=n.generators_t.p[n.generators.index[n.generators.carrier=='load']].sum(axis=1).max()
    df_rose.loc[sc,'Flexibility Usage']= h2+b2+bio
    
    df_rose.loc[sc,'Renewables Investments']= so+onw+ofw
    
    df_rose.loc[sc,'battery 2045 Energy']= b2
    df_rose.loc[sc,'Hydrogen 2045 Energy']= h2
    df_rose.loc[sc,'Biomass Utilization 2045']= bio
    
    df_rose.loc[sc,'Biomass Utilization']= gen_bar.biomass.sum()
    df_rose.loc[sc,'Fossil Fuel Utilization']= gen_bar[['CCGT','OCGT','oil','coal','lignite']].sum().sum()
    
    n=pypsa.Network('../data/{}/{}/{}.nc'.format(net,S,2050))
    acloading=abs(n.lines_t.p0/n.lines.loc[:,'s_nom']).mean().mean()*100
    
    df_rose.loc[sc,'Grid Loading']=acloading
    
    
    
    
    df_rose['Flexibility Investment']=df_rose[['Grid Development','Biomass Power','Battery Power','Hydrogen Power','Imbalance Power']].mean(axis=1)
    
    df_rose['Flexibility Potential']  = scenarios_settings.Flex
    df_rose['Flexibility Cost']  = scenarios_settings.Flex_cost*1000
    df_rose['Flexibility Duration']  = scenarios_settings.Max_hours
    
    df_rose.replace(np.NaN,0,inplace=True)
    



    df_rose.to_csv('../data/{}/{}_all_rose_data.csv'.format(net,net))




#%% plot 2 : Radar Best,Average,Worst,REF



cols=['Total System Cost','CO2 Emissions','Flexibility Investment','Flexibility Usage',
      'RES Curtailment','Fossil Fuel Utilization', 'Biomass Utilization','Renewables Investments',
      'Peak Reduction','SME Usage','SME Money','Imbalance Peak',
      'Spot Market','Grid Loading']



df_original = pd.DataFrame(0,index=['Optimal SME Settings'], columns=cols)

scs=['S52','S53','S84','S85']
df_original.loc['Optimal SME Settings']=df_rose.loc['S32']
df_original.loc['Sub-optimal SME Settings']=df_rose.loc[scs].mean()
df_original.loc['Pessimal SME Settings']=df_rose.loc['S97']
df_original.loc['No SME Flexibility']=df_rose.loc['S129']



d=df_original.copy()
d-=df_rose.loc['S129']

d.to_excel('../Results/{}/SME Impact - Table B1.xlsx'.format(net))



df= (df_original-df_original.mean())/df_original.std()

cols_sorted=['Total System Cost','CO2 Emissions','Fossil Fuel Utilization','Biomass Utilization',
             'Flexibility Investment', 'Flexibility Usage','RES Curtailment','Renewables Investments',
             'Peak Reduction','Imbalance Peak','Grid Loading','SME Usage', 
             'SME Money','Spot Market']

df=df[cols_sorted]

categories=list(df)
N = len(categories)
 
# What will be the angle of each axis in the plot? (we divide the plot / number of variable)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]


df*=-1

categories[0]='Lower System\nCost'
categories[1]='CO\N{SUBSCRIPT TWO} Abatement'
categories[2]='Reduced Fossil\nFuel Utilization'
categories[3]='Reduced\nBiomass\nUtilization'

categories[4]='Lower \nFlexibility\nInvestment'
categories[5]='Reduced Flexibility\nUsage'

categories[6]='Reduced Renewables\nCurtailment'
categories[7]='Lower Renewables\nInvestments'

categories[8]='Peak\nReduction'
categories[9]='Imbalance\nReduction'
categories[10]='Reduced\nGrid\nLoading'

categories[11]='SME\nUsage'
categories[12]='SME\nRevenue'
categories[13]='Wholesale\nPrice'


text=r'*: Values are normalized. The higher the values, the better the conditions turned out in the system'\
    ' i.e., lower system costs, lower CO\u2082 emissions, \nlower flexibility investment and usage, lower renewable energy'\
    ' curtailment and investments, lower fossil fuel and biomass utilization, lower peak \nload and imbalance power'\
        'lower wholesale price, lower grid loading'\
            'higher SME usage and revenue\nSME revenue and usage attributes are only for scenarios with SME flexibility'
# text=r"bold and italic: $\mathbfit{F_\alpha}$"
hfont = {'fontname':'Times New Roman'}
# df*=-1
cm=1/2.54
ax = plt.subplot(111, polar=True)
plt.gcf().set_size_inches(22, 10)
# plt.title("Impact of SME Flexibility Settings on The System Performance", fontsize=20,weight='bold')
ax.set_theta_offset(pi / 2)
ax.set_theta_direction(-1)
plt.xticks(angles[:-1], categories, size='xx-large',weight='bold',**hfont)
ax.tick_params(axis='x', which='major', pad=25)
for group in df.index:
    values=df[df.index==group].values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, linewidth=2, linestyle='solid', label="{}".format(group),color=colors[group])
    ax.fill(angles, values, 'b', alpha=0.1,color=colors[group])
ax.legend(loc='best', bbox_to_anchor=(1.2, 0.9),
           fancybox=True,fontsize=18,frameon=True,shadow=True)
# ax.legend().get_frame().set_linewidth(1.0)
ax.set_facecolor('gainsboro')
plt.text(0.35, 1, "Impact of SME Flexibility Settings on The System Performance $^{*}$",
         style='italic',weight='bold',
         fontsize=36, color='black',transform=plt.gcf().transFigure,**hfont)
plt.text(0.75, 0.5, r"Optimal SME Settings: high potential$\uparrow$, long duration$\uparrow$, and low cost$\downarrow$",
          fontsize=18, color='green',transform=plt.gcf().transFigure,weight='bold',**hfont)
plt.text(0.75, 0.46, r"Sub-optimal SME Settings: average potential$\updownarrows$, average duration$\updownarrows$, and average cost$\updownarrows$",
          fontsize=18, color='red',transform=plt.gcf().transFigure,weight='bold',**hfont)
plt.text(0.75, 0.42, r"Pessimal SME Settings: Low potential$\downarrow$, short duration$\downarrow$, and high cost$\uparrow$",
          fontsize=18, color='purple',transform=plt.gcf().transFigure,weight='bold',**hfont)
plt.text(0.31, -0.10, text,style='italic',**hfont,
          fontsize=22, color='black',transform=plt.gcf().transFigure)
plt.savefig('../Results/{}/Rose Abstract'.format(net),bbox_inches='tight',dpi=600)
plt.show()


ax = plt.subplot(111, polar=True)
plt.gcf().set_size_inches(22, 10)
# plt.title("Impact of SME Flexibility Settings on The System Performance", fontsize=20,weight='bold')
ax.set_theta_offset(pi / 2)
ax.set_theta_direction(-1)
plt.xticks(angles[:-1], categories, size='xx-large',weight='bold',**hfont)
ax.tick_params(axis='x', which='major', pad=25)
for group in df.index:
    values=df[df.index==group].values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, linewidth=2, linestyle='solid', label="{}".format(group),color=colors[group])
    ax.fill(angles, values, 'b', alpha=0.1,color=colors[group])
ax.legend(loc='best', bbox_to_anchor=(1.2, 0.9),
           fancybox=True,fontsize=18,frameon=True,shadow=True)
# ax.legend().get_frame().set_linewidth(1.0)
ax.set_facecolor('gainsboro')
plt.text(0.35, 1, "Impact of SME Flexibility Settings on The System Performance",
         style='italic',weight='bold',
         fontsize=36, color='black',transform=plt.gcf().transFigure,**hfont)
plt.savefig('../Results/{}/Rose Optimal'.format(net),bbox_inches='tight',dpi=600)
plt.show()




#%% plot 3 : Best Settings wrt REF


df_original = pd.DataFrame(0,index=['High SME Potential'], columns=cols)

df_original.loc['High SME Potential']=df_rose.loc[df_rose['Flexibility Potential']==20].mean()
df_original.loc['Long SME Duration']=df_rose.loc[df_rose['Flexibility Duration']==8].mean()
df_original.loc['Low SME Cost']=df_rose.loc[df_rose['Flexibility Cost']==10].mean()



d=df_original.copy()
d.loc['No SME Flexibility']=df_rose.loc['S129']
d.to_excel('../Results/{}/SME Impact - Table B1.xlsx'.format(net))

df_original-=df_rose.loc['S129']


df= (df_original-df_original.mean())/df_original.std()


cols_sorted=['Total System Cost','CO2 Emissions','Fossil Fuel Utilization','Biomass Utilization',
             'Flexibility Investment', 'Flexibility Usage','RES Curtailment','Renewables Investments',
             'Peak Reduction','Imbalance Peak','Grid Loading','SME Usage', 
             'SME Money','Spot Market']

df=df[cols_sorted]

categories=list(df)
N = len(categories)
 
categories[0]='Lower System\nCost'
categories[1]='CO\N{SUBSCRIPT TWO} Abatement'
categories[2]='Reduced Fossil\nFuel Utilization'
categories[3]='Reduced\nBiomass\nUtilization'

categories[4]='Lower \nFlexibility\nInvestment'
categories[5]='Reduced Flexibility\nUsage'

categories[6]='Reduced Renewables\nCurtailment'
categories[7]='Lower Renewables\nInvestments'

categories[8]='Peak\nReduction'
categories[9]='Imbalance\nReduction'
categories[10]='Reduced\nGrid\nLoading'

categories[11]='SME\nUsage'
categories[12]='SME\nRevenue'
categories[13]='Wholesale\nPrice'
# What will be the angle of each axis in the plot? (we divide the plot / number of variable)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]


df*=-1



ax = plt.subplot(111, polar=True)
plt.gcf().set_size_inches(22, 10)
plt.text(0.35, 1, "Impact of SME Flexibility Settings on The System Performance wrt REF Scenario",
         style='italic',weight='bold',
         fontsize=24, color='black',transform=plt.gcf().transFigure,**hfont)
ax.set_theta_offset(pi / 2)
ax.set_theta_direction(-1)
plt.xticks(angles[:-1], categories, size='xx-large',weight='bold',**hfont)
ax.tick_params(axis='x', which='major', pad=25)
for group in df.index:
    values=df[df.index==group].values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, linewidth=2, linestyle='solid', label="{}".format(group),color=colors[group])
    ax.fill(angles, values, 'b', alpha=0.1,color=colors[group])
ax.legend(loc='best', bbox_to_anchor=(1.2, 0.9),
           fancybox=True,fontsize=18,frameon=True,shadow=True)
# ax.legend().get_frame().set_linewidth(1.0)
ax.set_facecolor('gainsboro')
plt.savefig('../Results/{}/Rose SME Settings'.format(net),bbox_inches='tight',dpi=600)
plt.show()










#%%  Counting



(df_rose[cols] >df_rose.loc['S129',cols]).sum() ## 

"""
Total System Cost          26 scenarios are worse than REF
CO2 Emissions               2
Flexibility Investment     12
Flexibility Usage           0
RES Curtailment            14
Fossil Fuel Utilization     5
Biomass Utilization        35
Renewables Investments     61
Peak Reduction              2
SME Usage                   0
SME Money                   0
Imbalance Peak             48
Spot Market                12
Grid Loading               42
"""

(df_rose.loc[df_rose['Flexibility Potential']!=0].mean() > df_rose.loc[df_rose['Flexibility Potential']==0].mean() )[cols]

"""
with SME , the system was on average better off
Total System Cost          False
CO2 Emissions              False
Flexibility Investment     False
Flexibility Usage          False
RES Curtailment            False
Fossil Fuel Utilization    False
Biomass Utilization        False
Renewables Investments     False
Peak Reduction             False
SME Usage                  False
SME Money                  False
Imbalance Peak             False
Spot Market                False
Grid Loading               False

"""

d=df_rose.loc[df_rose['Flexibility Potential']!=0,cols] - df_rose.loc['S129',cols]

for col in cols:
    print(col)
    d.loc[:,col] = preprocessing.normalize([d[col]])[0]

d= (d-d.mean())/d.std()

fig,ax = plt.subplots(1,1)
fig.set_size_inches(26,12)
d.plot(kind='box',ax=ax)
plt.ylabel('Normalized Difference wrt REF scenario', fontsize=18)
ax.set_facecolor('gainsboro')
plt.grid(alpha=0.7)
plt.xticks(size=18)
plt.yticks(size=15)
# plt.savefig('Results/Scenarios Box.png', dpi=300)

