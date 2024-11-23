import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import ast
import folium
#import geopandas as gpd

cdr = pd.read_csv('RIKY/data/cdr_preprocessed.csv')
pdr = pd.read_csv('RIKY/data/pdr_processed.csv')

summary_df = cdr.groupby('EVSE ID').agg({
    'Potenza (kW)': 'first',
    'Station Città': 'first',
    'Ricavi totali (€) (IVA esclusa)': 'sum',
    'Ricavi Energia (€) (IVA esclusa)': 'sum',
    'Energia (kWh)': 'sum',
    'Tempo Totale (min)': 'sum'
}).reset_index()

##############-------------------- FIRST MERGE --------------------##############
merged_df = pdr.merge(summary_df, how='left', left_on='connector_evse_id', right_on='EVSE ID')
#################################################################################

#correlation
corr_matrix = merged_df.select_dtypes(include=['int64', 'float64']).corr()

fig, ax = plt.subplots(figsize=(20, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
ax.set_title(f'Heatmap of Correlation Matrix (without the CDR ID)')
plt.tight_layout()
plt.show()


#based on the correlation matrix and on previous analysis we drop some of the columns
columns_to_drop = [
    'totEnergyLocal', 'totEnergyNotLocal',
    'totSessionsLocal', 'totSessionsNotLocal',
    'Ricavi Energia (€) (IVA esclusa)', 'Energia (kWh)',
    'connector_connector_status_id', 'station_id',
    'connector_id', 'connector_station_id',
    'connector_uid', 'station_uid', 'station_model',
    'station_firmware', 'station_serial_number', 'station_installation_date',
    'station_is_visible', 'plugs', 'sessions', 'Anno', 'Mese',
]
# Drop these columns from your DataFrame
merged_df = merged_df.drop(columns=columns_to_drop)


#new correlation matrix after dropping the columns
corr_matrix = merged_df.select_dtypes(include=['int64', 'float64']).corr()

fig, ax = plt.subplots(figsize=(20, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
ax.set_title(f'Heatmap of Correlation Matrix (without the CDR ID)')
plt.tight_layout()
plt.show()

# adding the region and population

regioni = pd.read_csv('RIKY/data/regions_population.csv')
comuni = pd.read_csv('RIKY/data/gi_comuni_cap.csv', sep= ';')


#region's name are different in the two datasets, we have to change them in order to perform the joining
comuni_regions = sorted(comuni['denominazione_regione'].unique().tolist())
regioni_regions = sorted(regioni['Regione'].unique().tolist())

#check if the names of the regions are the same
differences = []
for index in range(min(len(comuni_regions), len(regioni_regions))):
    if comuni_regions[index] != regioni_regions[index]:
        differences.append((comuni_regions[index], regioni_regions[index]))
print("Differences:", differences)

#two regions are different, we have to change them
comuni['denominazione_regione'].replace(["Valle d'Aosta/Vallée d'Aoste", 'Trentino-Alto Adige/Südtirol'], ["Valle d'Aosta", 'Trentino-Alto Adige'], inplace = True)

##############-------------------- SECOND & THIRD MERGE --------------------##############
regions_and_population = regioni.merge(comuni[['cap', 'denominazione_provincia', 'ripartizione_geografica', 'denominazione_regione']], left_on='Regione', right_on = "denominazione_regione", how='right')
regions_and_population.drop_duplicates(inplace=True)
regions_and_population.drop(columns = ['denominazione_regione'], inplace=True)

merged_df = merged_df.merge(regions_and_population[regions_and_population.columns.tolist()], left_on= 'station_postal_code', right_on= 'cap', how='left')
merged_df.drop_duplicates(inplace = True, subset = 'connector_evse_id')
merged_df.isna().sum()

#check the missing values
rows_with_missing = merged_df[merged_df.isnull().any(axis=1)]

#handling missing data created afrter the merges
merged_df.loc[merged_df['station_city'].isin(['Modena', 'Parma']), 'Regione'] = 'Emilia-Romagna'
merged_df.loc[merged_df['station_city'] == 'Milano', 'Regione'] = 'Lombardia'
merged_df.loc[merged_df['station_city'] == 'Foggia', 'Regione'] = 'Puglia'

merged_df['Ricavi totali (€) (IVA esclusa)'] = merged_df['Ricavi totali (€) (IVA esclusa)'].fillna(merged_df['Ricavi totali (€) (IVA esclusa)'].mean())
merged_df['Tempo Totale (min)'] = merged_df['Tempo Totale (min)'].fillna(merged_df['Tempo Totale (min)'].mean())


merged_df.loc[(merged_df['Regione'] == 'Puglia') & (merged_df['Population'].isna()), 'Population'] = 3990891
merged_df.loc[(merged_df['Regione'] == 'Emilia-Romagna') & (merged_df['Population'].isna()), 'Population'] = 4467118
merged_df.loc[(merged_df['Regione'] == 'Lombardia') & (merged_df['Population'].isna()), 'Population'] = 10060574

merged_df = merged_df.drop(['EVSE ID', 'Station Città', 'denominazione_provincia', 'ripartizione_geografica'], axis=1)

merged_df.to_csv('RIKY/data/task_2_df.csv', index=False)

