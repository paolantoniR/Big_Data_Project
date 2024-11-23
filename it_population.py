
##### IMPORT LIBRARIES #####

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import wkt

##### IMPORT DATASETS #####

density = pd.read_csv('/Users/davidpaquette/Downloads/ita_general_2020.csv')
towns = pd.read_csv('/Users/davidpaquette/Downloads/it.csv')
regions = gpd.read_file('/Users/davidpaquette/Downloads/limits_IT_regions.geojson')
provinces = gpd.read_file('/Users/davidpaquette/Downloads/limits_IT_provinces.geojson')
municipalities = gpd.read_file('/Users/davidpaquette/Downloads/limits_IT_municipalities.geojson')

# Target demographic is men between ages 35-55
men = pd.read_csv('/Users/davidpaquette/Downloads/ita_men_2020.csv')

#POIs
pois = pd.read_csv('/Users/davidpaquette/Downloads/extracted_pois.csv')

##### Clustering #####

# Placeholder: Load the population density data
density_gdf = gpd.GeoDataFrame(density, geometry = gpd.points_from_xy(density.longitude, density.latitude), crs = "EPSG:4326")

### REGION

#Spatial join: Match each density point with an administrative region
regions_joined_gdf = gpd.sjoin(density_gdf, regions, how = "inner", predicate = "intersects")

# Aggregate population density by region
regions_aggregated_density = regions_joined_gdf.groupby('reg_name').agg({'ita_general_2020': 'sum'}).reset_index()

regions = regions.merge(regions_aggregated_density, on = 'reg_name', how = 'left')

regions = regions.rename(columns = {'ita_general_2020' : 'density'})

### PROVINCE

joined_gdf = gpd.sjoin(density_gdf, provinces, how = "inner", predicate = "intersects")

aggregated_density = joined_gdf.groupby('prov_name').agg({'ita_general_2020': 'sum'}).reset_index()

provinces = provinces.merge(aggregated_density, on = 'prov_name', how = 'left')

provinces = provinces.rename(columns = {'ita_general_2020' : 'density'})

### MUNICIPALITY

municipalities_joined_gdf = gpd.sjoin(density_gdf, municipalities, how = "inner", predicate = "intersects")

municipalities_aggregated_density = municipalities_joined_gdf.groupby('name').agg({'ita_general_2020': 'sum'}).reset_index()

municipalities = municipalities.merge(municipalities_aggregated_density, on = 'name', how = 'left')

municipalities = municipalities.rename(columns = {'ita_general_2020' : 'density'})

### MEN 

men_gdf = gpd.GeoDataFrame(men, geometry = gpd.points_from_xy(men.longitude, men.latitude), crs = "EPSG:4326")

# Region

m_regions_joined_gdf = gpd.sjoin(men_gdf, regions, how = "inner", predicate = "intersects")

m_regions_aggregated_density = m_regions_joined_gdf.groupby('reg_name').agg({'density': 'sum'}).reset_index()

men_region = regions.merge(m_regions_aggregated_density, on='reg_name').drop(columns='density_x').rename(columns={'density_y': 'men_density'})

men_region.drop(columns = ['reg_istat_code_num', 'reg_istat_code'])

# Province

m_province_joined_gdf = gpd.sjoin(men_gdf, provinces, how = "inner", predicate = "intersects")

m_provinces_aggregated_density = m_province_joined_gdf.groupby('prov_name').agg({'density': 'sum'}).reset_index()

men_province = provinces.merge(m_provinces_aggregated_density, on='prov_name').drop(columns='density_x').rename(columns={'density_y': 'men_density'})

# Municipality

m_municipality_joined_gdf = gpd.sjoin(men_gdf, municipalities, how = "inner", predicate = "intersects")

m_municipality_aggregated_density = m_municipality_joined_gdf.groupby('name').agg({'density': 'sum'}).reset_index()

men_municipality = municipalities.merge(m_municipality_aggregated_density, on='name').drop(columns='density_x').rename(columns={'density_y': 'men_density'})

### VISUALIZATIONS PER AREA

regions.plot(column = 'density', legend = True, cmap = 'viridis')
plt.show()

provinces.plot(column = 'density', legend = True, cmap = 'viridis')
plt.show()

municipalities.plot(column = 'density', legend = True, cmap = 'viridis')
plt.show()

men_region.plot(column = 'men_density', legend = True, cmap = 'viridis')
plt.show()

men_province.plot(column = 'men_density', legend = True, cmap = 'viridis')
plt.show()

men_municipality.plot(column = 'men_density', legend = True, cmap = 'viridis')
plt.show()

### POIs

pois['geometry'] = pois['geometry'].apply(wkt.loads)

pois_gdf = gpd.GeoDataFrame(pois, geometry='geometry', crs="EPSG:4326")

pois_gdf = pois_gdf[pois_gdf['geometry'].notna()]
pois_gdf = pois_gdf[pois_gdf.is_valid]

if pois_gdf.crs != regions.crs:
    pois_gdf = pois_gdf.to_crs(regions.crs)

pois_gdf = pois_gdf[pois_gdf.within(regions.geometry.union_all())]

pois_gdf['amenity'].isnull().sum()

fig, ax = plt.subplots(figsize=(10, 10))
regions.plot(ax=ax, color='lightgrey', edgecolor='black')
pois_gdf.plot(ax=ax, column='amenity', legend=True, cmap='Set1', markersize=10)
plt.show()


# Separate points and polygons into different GeoDataFrames
points_gdf = pois_gdf[pois_gdf.geometry.type == 'Point']
polygons_gdf = pois_gdf[pois_gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])]

polygons_projected = polygons_gdf.to_crs("EPSG:32632")

# For polygons, calculate the centroid and replace the geometry
polygons_gdf['geometry'] = polygons_gdf.centroid

polygons_centroids = polygons_projected.to_crs("EPSG:4326")

# Now combine points_gdf and polygons_gdf back into a single GeoDataFrame
combined_gdf = pd.concat([points_gdf, polygons_gdf], ignore_index=True)

fig, ax = plt.subplots(figsize=(10, 10))
regions.plot(ax=ax, color='lightgrey', edgecolor='black')
combined_gdf.plot(ax=ax, column='amenity', legend=True, cmap='Set1', markersize=10)
plt.show()

