# -*- coding: utf-8 -*-
"""sharedmobility_validation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/nrohrbach/sharedmobility_monitoring/blob/main/sharedmobility_validation.ipynb

# Sharedmobility.ch - Validation of GBFS-Feeds
"""

#pip install datetime

import requests
import pandas as pd
from datetime import datetime, timezone
import json
import pytz

# GBFS Feeds abfragen
url = 'https://sharedmobility.ch/v2/gbfs'
header = {"Authorization":"geoinformation@bfe.admin.ch"}
feeds = requests.get(url, headers=header).json()

# Alle GBFS Feeds als Dataframe laden
id = [s['id'] for s in feeds['systems']]
url = [s['url'] for s in feeds['systems']]
gbfsfeeds = pd.DataFrame(list(zip(id, url)),columns =['provider', 'gbfsurl'])
providers = list(gbfsfeeds['provider'])

# Validieren!
JsonResponse = []

for provider in providers:
    try:
      headers = {
          'accept': '*/*',
          'Content-Type': 'application/json',
          'User-Agent': 'geoinformation@bfe.admin.ch',
      }

      json_data = {
          'url': 'https://sharedmobility.ch/v2/gbfs/'+ provider +'/gbfs',
          'options': {
              'freefloating': False,
              'docked': False,
              'version': None,
              'auth': {
                  'type': None,
                  'basicAuth': {
                      'user': None,
                      'password': None,
                  },
                  'bearerToken': {
                      'token': None,
                  },
                  'oauthClientCredentialsGrant': {
                      'user': None,
                      'password': None,
                      'tokenUrl': None,
                  },
              },
          },
      }
      response = requests.post('https://gbfs-validator.netlify.app/.netlify/functions/validator', headers=headers, json=json_data).json()

      JsonResponse.append(response)

    except:
      JsonResponse.append(response)

#Dataframe mit Resultaten bearbeiten
ValidationResults = pd.json_normalize(JsonResponse)
ValidationResults['provider'] = providers
ValidationResults['Validator'] = 'https://gbfs-validator.netlify.app/validator?url=https://gbfs.prod.sharedmobility.ch/v2/gbfs/'+ ValidationResults['provider']+'/gbfs'

# Add Timestamp
ValidationDatum = datetime.today()
ValidationDate = ValidationDatum.astimezone(pytz.timezone('Europe/Berlin')).strftime("%Y-%m-%d")
ValidationZeit = ValidationDatum.astimezone(pytz.timezone('Europe/Berlin')).strftime("%Y-%m-%d %H:%M")
ValidationResults['Date'] = ValidationDate

# Save as CSV
ValidationResults = ValidationResults.drop(columns=['files','summary.validatorVersion','summary.version.detected'])
ValidationResults.to_csv("data/GBFS_validated.csv",header=False,index=False, mode='a')

"""# Create Statusbadges für Übersicht auf Github"""

# Funktion die den Farbcode zuweist.
def CreateBadgeColour(row):
  if row['summary.hasErrors']:
    return "red"
  else:
    return "green"

# Badge erstellen
ValidationResults['Colour']= ValidationResults.apply(lambda row: CreateBadgeColour(row), axis=1)
ValidationResults['Badge']= '- [![Dokumentation](https://badgen.net/badge/' + ValidationResults['provider'] + '/' + ValidationResults['summary.errorsCount'].astype(str) + '%20errors/' + ValidationResults['Colour'] + '?icon=github)](' + ValidationResults['Validator'] + ')'
ValidationResults = ValidationResults.drop(columns=['summary.version.validated','summary.hasErrors','summary.errorsCount','provider', 'Validator', 'Date','Colour'])

# Add Timestamp to DataFrame
Timestamp = 'Last Update: '+ ValidationZeit
new_row = pd.DataFrame([' ',Timestamp], columns=['Badge'])
ValidationResults = pd.concat([ValidationResults, new_row], ignore_index=True)

# Save as MD-File
ValidationResults = ValidationResults.rename(columns={'Badge': '# Validation of all GBFS-Feeds'})
ValidationResults.to_csv('Validation.md', columns= ['# Validation of all GBFS-Feeds'], header=True, index=False)