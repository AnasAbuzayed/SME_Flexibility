# Code for the paper "Flexibility Matters: Impact assessment of Small and Medium Enterprises Flexibility on the German Energy Transition"
This repository contains the code and manuscript accompanying the paper "Flexibility Matters: Impact assessment of Small and Medium Enterprises Flexibility on the German Energy Transition".

# Abstract
This study analyzes the transition of the German electricity system towards climate neutrality by 2045, considering the demand-flexibility from small and medium enterprises (SMEs). Using an expansion model, a massive shift to renewable energy is required, primarily from solar and wind, with storage technologies playing a crucial role. The research uncovers the potential of flexibility from often-overlooked industrial SME sector, challenging their historical neglect in energy models and national strategies. As Germany stands at the crossroads of decarbonization, this study emphasizes the indispensable role of SMEs in shaping a resilient and flexible energy system. Despite representing only a small fraction of peak load, SME flexibility contributes to a significant reduction in carbon emissions and transition costs, as well as a decreased reliance on other flexibility measures. However, careful design and incentivization strategies are vital to reap the full benefits of SME flexibility. 

Challenges in achieving a secure electricity supply during extreme weather conditions in a 100% renewable system are identified, along with how SME flexibility helps to achieve climate neutrality. By 2045, wind power becomes vital for supply security and is operated as a dispatchable ramping-up technology. Storage flexibility, especially from batteries and hydrogen, becomes essential. The transition incurs substantial costs but is economically advantageous in the long run. Overcapacities from renewables allow for a higher degree of electrification, stronger sector coupling, and suggest the possibility of a local hydrogen production. The study provides valuable insights into how SME demand response can contribute to achieving a sustainable energy system, as well as the dynamics of a sustainable energy system, emphasizing the role of renewables and flexibilities.

<img src="/Results/16/Rose Abstract.png"/>


# Repository Structure

- `config.yaml` configuration data for the different scenarios and plotting.
- `codes` contains the .py files used for the evaluation of results.
- `paper` contains the `.docs` file for the paper.
- `Results` contains the results for the paper.

# Analysis Reproducing 
The analysis in this paper are fully reproducable using the `codes` and `data` folders in this repository

# Results Reproducing 
The paper's results are fully reproducable using  [MyPyPSA-Ger](https://github.com/AnasAbuzayed/MyPyPSA-Ger) model.
The impact of SME flexibility was invetigated using a 16-node network for Germany, produced from  [PyPSA-Eur](https://pypsa-eur.readthedocs.io). 
SME Flexibility is added using two open-source datasets:  [DemandRegio](https://github.com/DemandRegioTeam/disaggregator) and  [SyntheticLoadProfiles](https://github.com/asandhaa/SyntheticLoadProfiles)

