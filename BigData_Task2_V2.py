###### IMPORT LIBRARIES ######

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import wkt
from shapely.geometry import Point
from shapely.wkt import loads

###### IMPORT DATASETS ######

pois = pd.read_csv('/Users/davidpaquette/Downloads/800m_pois.csv')
ftx = pd.read_csv('/Users/davidpaquette/Downloads/riky_final.csv')
competitors = pd.read_csv('/Users/davidpaquette/Downloads/pun_data.csv', sep = ';')
density = pd.read_csv('/Users/davidpaquette/Downloads/ita_general_2020.csv')
regions = gpd.read_file('/Users/davidpaquette/Downloads/limits_IT_regions.geojson')
cars = pd.read_csv('/Users/davidpaquette/Downloads/macchine_aci.csv')

###### PREPROCESSING & OTHER SHIT ######

### POIs

pois['geometry'] = pois['geometry'].apply(lambda x: loads(x) if isinstance(x, str) and x.startswith('POINT') else x)

pois['geometry'] = pois['geometry'].apply(lambda x: Point(x) if isinstance(x, (tuple, list)) and len(x) == 2 else x)

pois = gpd.GeoDataFrame(pois, geometry = 'geometry', crs = 'EPSG:4326')

pois['geometry'] = pois['geometry'].apply(lambda point: Point(point.y, point.x))

### FTX

ftx = gpd.GeoDataFrame(ftx, geometry = gpd.points_from_xy(ftx.station_coordinates_lat, ftx.station_coordinates_lon), crs = "EPSG:4326")

### COMPETITORS

competitors = competitors[competitors['businessName'] != 'Free To X S.p.A.']

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
competitors = correct_coordinates_format(competitors)

competitors['coordinates.latitude'].astype('float')
competitors['coordinates.longitude'].astype('float')

competitors = competitors.rename(columns = {'coordinates.latitude' : 'latitude', 'coordinates.longitude' : 'longitude'})

competitors = gpd.GeoDataFrame(competitors, geometry = gpd.points_from_xy(competitors.latitude, competitors.longitude), crs = 'EPSG:4326')

### CAZZO DI SJOIN

# Convert both GeoDataFrames to the same projected CRS with meters as units
pois = pois.to_crs(epsg=3857)
ftx = ftx.to_crs(epsg=3857)
competitors = competitors.to_crs(epsg=3857)

# Create a buffer of 800 meters around each point in pois
pois['geometry'] = pois.geometry.buffer(800)

# First spatial join between pois and ftx
final_df = gpd.sjoin(pois, ftx, how='inner', predicate='intersects')

# Drop or rename the `index_right` column from the first join
final_df = final_df.drop(columns='index_right')

#final_df = gpd.sjoin(final_df, competitors, how='inner', predicate='intersects')

# Step 1: Create dummy variables for each unique amenity type
final_df['amenity'] = final_df['amenity'].str.strip().str.lower()  # Clean amenity column for consistency

# Convert 'amenity' column to dummy variables
amenity_dummies = pd.get_dummies(final_df['amenity'], prefix='amenity')

# Concatenate dummy variables with the original DataFrame
final_df = pd.concat([final_df.drop(columns='amenity'), amenity_dummies], axis=1)

final_df['connector_evse_id'] = final_df['connector_evse_id'].str.rsplit(pat = '*',n= 1).str[0]

final_df_collapsed = final_df.groupby('connector_evse_id').agg(
    {
        **{col: 'max' for col in amenity_dummies.columns},  # Take max for each dummy variable
        **{col: 'first' for col in final_df.columns if col not in amenity_dummies.columns and col != 'connector_evse_id'}  # Keep first instance for other columns
    }
).reset_index()

final_df_collapsed = gpd.GeoDataFrame(final_df_collapsed, geometry='geometry', crs='EPSG:3857')

# Step 4: Apply 800m buffer around each charging station
final_df_collapsed['buffered_geometry'] = final_df_collapsed.geometry.buffer(800)

# Step 5: Spatial join to count competitors within the 800m buffer
final_df_collapsed = final_df_collapsed.set_geometry('buffered_geometry')
competitor_counts = gpd.sjoin(final_df_collapsed, competitors, op='contains').groupby('connector_evse_id').size()

# Step 6: Merge the competitor counts back to the collapsed dataset
final_df_collapsed['competitor_count'] = final_df_collapsed['connector_evse_id'].map(competitor_counts).fillna(0).astype(int)

# Drop the buffer geometry column if no longer needed
final_df_collapsed = final_df_collapsed.drop(columns=['buffered_geometry'])

# Display the final DataFrame with competitor counts
final_df_collapsed.head()

### ADDING POPULATION

# Placeholder: Load the population density data
density_gdf = gpd.GeoDataFrame(density, geometry = gpd.points_from_xy(density.longitude, density.latitude), crs = "EPSG:4326")

#Spatial join: Match each density point with an administrative region
regions_joined_gdf = gpd.sjoin(density_gdf, regions, how = "inner", predicate = "intersects")

# Aggregate population density by region
regions_aggregated_density = regions_joined_gdf.groupby('reg_name').agg({'ita_general_2020': 'sum'}).reset_index()

regions = regions.merge(regions_aggregated_density, on = 'reg_name', how = 'left')

regions = regions.rename(columns = {'ita_general_2020' : 'density'})

# Merge the density data into final_df_collapsed based on region names
final_df_collapsed = final_df_collapsed.merge(
    regions[['reg_name', 'density']],
    how='left',
    left_on='denominazione_regione',  # Column in final_df_collapsed
    right_on='reg_name'               # Column in regions_df
)

# Drop redundant 'reg_name' column if needed
final_df_collapsed = final_df_collapsed.drop(columns=['reg_name'])

### Add cars

cars = cars.rename(columns={'Totale_macchine_interessate': 'total_machines'})

# Merge the two DataFrames on the region columns
final_df_collapsed = final_df_collapsed.merge(
    cars[['Regione', 'total_machines']],
    how='left',
    left_on='denominazione_regione',  # Column in final_df_collapsed
    right_on='Regione'                # Column in macchine_aci_df
)

# Drop the 'Regione' column after merging, if it's no longer needed
final_df_collapsed = final_df_collapsed.drop(columns=['Regione'])

# Final dataset
final_df_collapsed.to_csv('/Users/davidpaquette/Downloads/final_df.csv')