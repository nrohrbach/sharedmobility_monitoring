# -*- coding: utf-8 -*-
"""sharedmobility_monitoring.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/nrohrbach/sharedmobility_monitoring/blob/main/sharedmobility_monitoring.ipynb

# Monitoring GBFS-Feeds on sharedmobility.ch

Beschreibung...
"""

#pip install datetime

import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# GBFS Feeds abfragen
url = 'https://sharedmobility.ch/v2/gbfs'
header = {"Authorization":"geoinformation@bfe.admin.ch"}
feeds = requests.get(url,headers=header).json()

# Alle GBFS Feeds als Dataframe laden
id = [s['id'] for s in feeds['systems']]
url = [s['url'] for s in feeds['systems']]
gbfsfeeds = pd.DataFrame(list(zip(id, url)),columns =['provider', 'gbfsurl'])
providers = list(gbfsfeeds['provider'])

"""## Auswertung pro Provider"""

# Auswertung station_status.json
providerList = []
VehiclesInStationList = []
NumberOfStationsList = []

for provider in providers:
  try:
      stationstatus = requests.get('https://sharedmobility.ch/v2/gbfs/' + provider +'/station_status',headers=header).json()
      stationstatus = [s['num_bikes_available'] for s in stationstatus['data']['stations']]
      VehiclesInStationList.append(sum(stationstatus))
      NumberOfStationsList.append(len(stationstatus))
      providerList.append(provider)
  except:
      VehiclesInStationList.append('nan')
      NumberOfStationsList.append('nan')
      providerList.append(provider)

# Dataframe erstellen
dict = {'Provider': providerList, 'NumberOfStations': NumberOfStationsList, 'VehiclesInStation': VehiclesInStationList}
dfStationStatus = pd.DataFrame(dict)

# Auswertung free_bike_status.json
providerList = []
FreeBikeList = []

for provider in providers:
  try:
      freebikesstatus = requests.get('https://sharedmobility.ch/v2/gbfs/' + provider +'/free_bike_status',headers=header).json()
      freebikesstatus = [s['bike_id'] for s in freebikesstatus['data']['bikes']]
      FreeBikeList.append(len(freebikesstatus))
      providerList.append(provider)
  except:
      FreeBikeList.append('nan')
      providerList.append(provider)

# Dataframe erstellen
dict = {'Provider': providerList, 'NumberOfFreeBikes': FreeBikeList}
dfFreeBikes = pd.DataFrame(dict)

# Dataframe zusammenführen und speichern
dfMonitoring = pd.merge(dfStationStatus, dfFreeBikes, how="left", on=["Provider"])
dfMonitoring['Date'] = datetime.today().strftime("%Y-%m-%d")

#Speichern
dfMonitoring.to_csv("data/Sharedmobility_Providers.csv", header=False, index=False, mode='a')

#Visualisierung
df = pd.read_csv("data/Sharedmobility_Providers.csv", parse_dates=['Date'])
df = df.fillna(0)

# LineChart mit Anzahl Fahrzeugen und Anzahl Stationen

for provider in providers:
  try:
    df_provider = df[df['Provider']==provider]
    df_provider = df_provider.pivot(index="Date", columns=["Provider"], values=['NumberOfStations','VehiclesInStation','NumberOfFreeBikes'])
    df_provider.plot(figsize=(15,10))
    plt.legend(loc='best')
    plt.title("Anzahl Fahrzeuge und Stationen: "+ provider)
    plt.savefig('plots/' + provider + '.png')
    plt.close()
  except:
    plt.savefig('plots/' + provider + '.png')

