import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

data = pd.read_csv('/Users/davidpaquette/Downloads/pun_data.csv', sep = ';')
regions = gpd.read_file('/Users/davidpaquette/Downloads/limits_IT_regions.geojson')

def correct_coordinates_format(data):
    # Funzione per correggere il formato di una singola coordinata
    def fix_coordinate_format(coord):
        # Controlla se è una stringa
        if isinstance(coord, str):
            # Divide la stringa in base ai punti
            parts = coord.split('.')
            if len(parts) > 2:
                # Unisce solo il primo e secondo elemento con un punto, il resto come parte decimale senza punti extra
                coord = '.'.join([parts[0], parts[1]]) + ''.join(parts[2:])
            else:
                # Se c'è solo un punto, lascia il formato così com'è
                coord = '.'.join(parts)
        return coord

    # Applica la correzione alle colonne latitudine e longitudine
    data['coordinates.latitude'] = data['coordinates.latitude'].apply(fix_coordinate_format)
    data['coordinates.longitude'] = data['coordinates.longitude'].apply(fix_coordinate_format)

    return data

# Applica la funzione di correzione al dataset
data = correct_coordinates_format(data)

data['coordinates.latitude'].astype('float')
data['coordinates.longitude'].astype('float')

data = data.rename(columns = {'coordinates.longitude' : 'longitude', 'coordinates.latitude' : 'latitude'})

data_gdf = gpd.GeoDataFrame(data, geometry = gpd.points_from_xy(data.longitude, data.latitude), crs = 'EPSG:4326')

regions_joined_gdf = gpd.sjoin(data_gdf, regions, how = "inner", predicate = "intersects")

# Group by region name and count chargers
charger_counts_by_region = regions_joined_gdf.groupby('reg_name').size().reset_index(name='charger_count').sort_values(by='charger_count', ascending=False).reset_index(drop=True)

# Group by region name and count chargers
charger_counts_by_region_and_business = regions_joined_gdf.groupby(['reg_name', 'businessName']).size().reset_index(name='charger_count')

pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)  # Adjust display width to fit all columns

print(charger_counts_by_region_and_business)

# Plotting
fig, ax = plt.subplots(figsize=(10, 10))

# Plot the regions
regions.plot(ax=ax, color='lightgrey', edgecolor='black')

# Plot the points
regions_joined_gdf.plot(ax=ax, color='blue', markersize=5, label='Chargers')


#### GRAPHS

companies = regions_joined_gdf.groupby('businessName').size().reset_index(name = 'company_count').sort_values(by='company_count', ascending=False).reset_index(drop=True)

# Increase figure size for better readability
plt.figure(figsize=(12, 6))

# Create the bar plot
plt.bar(companies['businessName'], companies['company_count'], color='#4CA3DB')

# Add titles and labels
plt.title("Distribution of Chargers per Company", fontsize=16)
plt.xlabel("Company", fontsize=12)
plt.ylabel("Number of Chargers", fontsize=12)

# Rotate x-axis labels and adjust layout
plt.xticks(rotation=45, ha='right')
plt.tight_layout()  # Adjust layout to prevent label cutoff

# Display the plot
plt.show()

chargers_per_region = charger_counts_by_region.nlargest(10, 'charger_count')

# Increase figure size for better readability
plt.figure(figsize=(12, 6))

# Create the bar plot
plt.bar(chargers_per_region['reg_name'], chargers_per_region['charger_count'], color='#4CA3DB')

# Add titles and labels
plt.title("Top 10 Regions with Most Chargers", fontsize=16)
plt.xlabel("Region", fontsize=12)
plt.ylabel("Number of Chargers", fontsize=12)

# Rotate x-axis labels and adjust layout
plt.xticks(rotation=45, ha='right')
plt.tight_layout()  # Adjust layout to prevent label cutoff

# Display the plot
plt.show()
