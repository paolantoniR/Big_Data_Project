import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import folium

data = pd.read_csv('dataset/full/pdr_locations.csv')

data.shape

valori_mancanti = [0, -1, 'unknown', 'UNK', 'N/A', 'NA', 'nan', 'NULL', '', ' ', '?', '-999', 'None']

data.isnull().sum().sum()

# Sostituisci questi valori con NaN
data_null = data.replace(valori_mancanti, np.nan)
data_null.isnull().sum().sum()

# display of heatmap to see null columns
colors = ['#4CA3DB',"#EBBA41"]  # missing values, non-missing values
cmap = mcolors.ListedColormap(colors)

# Plot heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(data_null.isnull(), cbar=False, cmap=cmap)
plt.title("Distribution of Null Values in PDR before dropping null columns")
plt.ylabel('Observations')
plt.xlabel('Variables')
plt.tight_layout()
plt.savefig('plots/null_values_before_dropping.png', dpi=600)
plt.show()




# select the columns that are null
data_null_names = data_null.isnull().sum()
data_null_names = data_null_names[data_null_names == data.shape[0]]
data_null_names = data_null_names.to_frame()

# drop null columns
data_no_null = data.drop(columns=data_null_names.index)

# display columns that still present null values
colors = ['#4CA3DB',"#EBBA41"]  # missing values, non-missing values
cmap = mcolors.ListedColormap(colors)

# Plot heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(data_no_null.isnull(), cbar=False, cmap=cmap)
plt.title("Distribution of Null Values in PDR before dropping null columns")
plt.ylabel('Observations')
plt.xlabel('Variables')
plt.tight_layout()
plt.savefig('plots/null_values_before_dropping.png', dpi=600)
plt.show()

null_columns_list = data_no_null.columns[data_no_null.isnull().any()] # columns that still contain null values
print(null_columns_list)

#analysis for single columns

# station_brand
data_no_null['station_brand'].value_counts()
print('number of missing values in station_brand:', data_no_null['station_brand'].isnull().sum())
station_brand_missing = data_no_null[data_no_null['station_brand'].isna()]
# when ths station brand is missing also 'station_model', 'station_firmware', 'station_serial_number'
# are missing values (79 missing values)
# ---> best choice is to change the value to something else in order to not lose information about charging points?
# Replace NaN values with 'UNKNOWN' without inplace=True


# station model
data_no_null['station_model'].value_counts()
data_no_null['station_model'].nunique()

# station firmware
data_no_null['station_firmware'].value_counts()
data_no_null['station_firmware'].nunique()

# 'station_serial_number'
data_no_null['station_serial_number'].value_counts()
data_no_null['station_serial_number'].nunique()

# station_type_status
data_no_null['station_type_status'].isna().sum()
data_no_null['station_type_status'].value_counts()
station_null_rows = data_no_null[data_no_null['station_type_status'].isnull()]
data_no_null[data_no_null['station_id'] == 1033694]
data_no_null['station_type_status'] = data_no_null['station_type_status'].replace(np.nan, 'public')  # change with most common class

# drop 'station_commissioning_date' che contengono tanti tanti null
data_no_null = data_no_null.drop(columns=['station_commissioning_date'], axis=0)

data_no_null.info()

# change id columns from integers to strings
id_columns = [col for col in data_no_null.columns if col.endswith('_id') or col.endswith('_uid')]
data_no_null[id_columns] = data_no_null[id_columns].astype(str)
data_no_null.info()

########################################rows with null values, to see why they have null values
rows_with_nulls = data_no_null[data_no_null.columns[data_no_null.isnull().any(axis=0)]]

plt.figure(figsize=(12, 8))
sns.heatmap(rows_with_nulls.isnull(), cbar=False, cmap='viridis')
plt.title("Distribuzione dei valori mancanti (NaN) nel dataset CDR")
plt.show()

# change the null values in a new value called UNKNOWN
columns_to_replace = ['station_brand', 'station_model', 'station_firmware', 'station_serial_number']
data_no_null[columns_to_replace] = data_no_null[columns_to_replace].fillna('UNKNOWN')

# station_installation_date is the only column with missing values (122)




########--------- END OF MISSING VALUES HANDLING --------############
########--------- Analysis per type --------############
########--------- Numeric --------############




data_no_null.info()

data_numerical = data_no_null.select_dtypes(include=['int64', 'float64'])

data_numerical_stats = data_numerical.describe()

# station_postal_code
data_numerical['station_postal_code'].nunique()

# Plotting latitude and longitude on a scatter plot
plt.figure(figsize=(8, 6))
plt.scatter(data_numerical['station_coordinates_lon'], data_numerical['station_coordinates_lat'], c='blue', marker='o')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Locations based on Latitude and Longitude')
plt.show()

####VEDERE SE totSessions e totPublicSessions sono uguali
are_columns_equal = data_numerical['totSessions'].equals(data_numerical['totPublicSessions'])
print('Are totSessons and totPublicSessions columns equal:', are_columns_equal)

# Drop totPublicSessions

data_no_null = data_no_null.drop(columns=['totPublicSessions'], axis=0)
data_numerical = data_numerical.drop(columns=['totPublicSessions'], axis=0)

# removing the variables that have standard deviation equal to 0 (univariate columns)
std_dev = data_numerical.std(axis=0)
zero_std_columns = std_dev[std_dev == 0].index.tolist()
data_no_null = data_no_null.drop(columns=zero_std_columns)
data_numerical = data_numerical.drop(columns=zero_std_columns)

#################------------------ STRING/OBJECTS---------#####################

data_string = data_no_null.select_dtypes(include='object')


def constant_columns(df):
    # List to store columns with the same value for all observations
    constant_cols = []

    # Iterate over columns in the dataframe
    for col in df.columns:
        # Check if the column contains only one unique value
        if df[col].nunique() == 1:
            constant_cols.append(col)

    return constant_cols


constant_columns_string = constant_columns(data_string)

# drop columns that are constant

data_no_null = data_no_null.drop(columns=constant_columns_string, axis=0)

'''
here we exploded the variable plugs but a further analysis showed how the most important information were summarized
in other colsumns

plugs_df = data_string['plugs']
plugs_df = plugs_df.to_frame()

df_expanded = pd.DataFrame(plugs_df['plugs'].apply(lambda x: x[0]).tolist())
'''

###############---------- VARIABILI BULEANE--------###############
data_bool = data_no_null.select_dtypes(include='bool')
constant_columns_bool = constant_columns(data_bool)
data_no_null = data_no_null.drop(columns=constant_columns_bool, axis=0)


##########------- altre analisi---------########
data_no_null['new_evse_id'] = data_no_null['connector_evse_id'].str.rsplit(pat = '*',n= 1).str[0]
#here we create a new column called new_evse_id that is the connector_evse_id but without the identifier for the single
#plug, and we do it by dropping the last two characters from this code, example 'IT*F2X*EF2XITMPXP51*1' to 'IT*F2X*EF2XITMPXP51'



# List of values to check
values_to_check = ['IT*F2X*EF2XITMPXP51', 'IT*F2X*EF2XITMPXP51',
                   'IT*F2X*EF2XITMPXP01', 'IT*F2X*EF2XITMPXP01',
                   'IT*F2X*EITDGRM00001']

# Check if values in 'connector_evse_id' column are in the list
matching_rows = data_no_null[data_no_null['new_evse_id'].isin(values_to_check)]

# Display the matching rows
if not matching_rows.empty:
    print("The following rows contain the specified values in 'connector_evse_id':")
    print(matching_rows)
else:
    print("None of the specified values were found in 'connector_evse_id'.")





#Here we started a temporal analysis, but in the later steps we didn't use any temporal data

data_no_null['station_installation_date'] = pd.to_datetime(data_no_null['station_installation_date'], errors='coerce')


# Estrai l'anno e il mese dalle date
data_no_null['Anno'] = data_no_null['station_installation_date'].dt.year
data_no_null['Mese'] = data_no_null['station_installation_date'].dt.month

data_no_null['Anno'] = data_no_null['Anno'].fillna(0).astype('int64')
data_no_null['Mese'] = data_no_null['Mese'].fillna(0).astype('int64')

# Verifica i dati disponibili per ogni anno e mese
dati_per_anno_mese = data_no_null.groupby(['Anno', 'Mese']).size().unstack(fill_value=0)

# Mostra i risultati
print("Numero di ricariche per ciascun anno e mese:")
print(dati_per_anno_mese)


data_no_null.to_csv('RIKY/data/pdr_processed.csv', index=False)





