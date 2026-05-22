from fastapi import APIRouter
import geopandas as gpd
from shapely.geometry import Point
import json

router = APIRouter()

@router.get("/geo-data")
def get_geo_data():

    gdf = gpd.read_file("../data/sample.geojson")

    return json.loads(gdf.to_json())


@router.get("/nearby")
def nearby_locations(lat: float, lon: float):

    gdf = gpd.read_file("../data/sample.geojson")

    user_point = Point(lon, lat)

    nearby = []

    for _, row in gdf.iterrows():

        geom = row.geometry

        distance = geom.distance(user_point)

        if distance < 0.05:

            nearby.append({
                "name": row["name"],
                "risk_level": row["risk_level"],
                "distance": distance
            })

    return {"nearby_locations": nearby}


@router.get("/risk-check")
def risk_check(lat: float, lon: float):

    gdf = gpd.read_file("../data/sample.geojson")

    user_point = Point(lon, lat)

    results = []

    for _, row in gdf.iterrows():

        polygon = row.geometry

        if polygon.contains(user_point):

            results.append({
                "region": row["name"],
                "risk_level": row["risk_level"],
                "status": "INSIDE RISK ZONE"
            })

    if not results:
        return {
            "status": "SAFE AREA"
        }

    return {
        "results": results
    }