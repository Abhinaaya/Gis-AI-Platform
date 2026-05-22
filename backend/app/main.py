from fastapi import FastAPI
import geopandas as gpd

app = FastAPI()

@app.get("/")
def home():
    return {"message": "GIS AI Platform Running"}

@app.get("/geo-data")
def get_geo_data():

    gdf = gpd.read_file("../data/sample.geojson")
    import json

    return json.loads(gdf.to_json())

