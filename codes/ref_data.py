# -*- coding: utf-8 -*-
"""
© Anas Abuzayed 2023  <anas.abuzayed@hs-offenburg.de>
This code to download the data for the reference scenario (without SME)
"""

import pypsa
import os
import requests
from zipfile import ZipFile
import yaml
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
with open(r'../config.yaml') as file:
    config= yaml.load(file, Loader=yaml.FullLoader)

createFolder('../data/'+str(config['scenario']['clusters']) + '/'+ config['scenario']['ref'])


os.chdir('../data/'+str(config['scenario']['clusters']) + '/'+ config['scenario']['ref'])

record_id = "10430721" ##pending acceptance in Zenodo

r = requests.get(f"https://zenodo.org/api/records/{record_id}")
download_urls = [f['links']['self'] for f in r.json()['files']]
filenames = [f['key'] for f in r.json()['files']]


for filename, url in zip(filenames, download_urls):
    print("Downloading:", filename)
    r = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(r.content)
