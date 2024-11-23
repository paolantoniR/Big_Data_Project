import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import ast
import folium
#import geopandas as gpd

df  = pd.read_csv('RIKY/data/task_2_df.csv')
macchine = pd.read_csv('RIKY/data/valori_macchine_elettriche.csv').drop(columns=['Unnamed: 0'], axis=1)


df_regions = sorted(df['Regione'].unique().tolist())
macchine_regions = sorted(macchine['Region'].unique().tolist())

macchine['Region'].replace(["Emilia Romagna", 'Friuli Venezia Giulia'], ["Emilia-Romagna", 'Friuli-Venezia Giulia'], inplace = True)


## MERGE ##
merged_df = df.merge(macchine, how='left', left_on='Regione', right_on = 'Region')
merged_df.drop(columns=['Region', 'totPublicEnergy', 'totPublicCost', 'connector_status'], inplace=True, axis=1)

merged_df = merged_df.rename(columns={'Value': 'EV_percentage_per_region'})
merged_df.to_csv('RIKY/data/riky_final.csv', index=False)