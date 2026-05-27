import geopandas as gpd

# read kml
gdf = gpd.read_file("../data/d6d078ca-7330-4efe-8a5f-0c74cb6a0a70.kml")

# save as geojson
gdf.to_file("../data/flood_points.geojson", driver="GeoJSON")

print("KML converted successfully!")