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
@router.get("/risk-summary")
def risk_summary(lat: float, lon: float):

    gdf = gpd.read_file("../data/sample.geojson")

    user_point = Point(lon, lat)

    for _, row in gdf.iterrows():

        polygon = row.geometry

        if polygon.contains(user_point):

            risk_level = row["risk_level"]

            if risk_level == "high":
                return {
                    "summary": "High flood risk detected near this location."
                }

            elif risk_level == "medium":
                return {
                    "summary": "Moderate flood risk detected near this location."
                }

            else:
                return {
                    "summary": "Low flood risk detected near this location."
                }

    return {
        "summary": "This location appears to be in a safe area."
    }
@router.get("/statistics")
def statistics():

    gdf = gpd.read_file("../data/sample.geojson")

    total_regions = len(gdf)

    high_risk = 0
    medium_risk = 0
    low_risk = 0

    for _, row in gdf.iterrows():

        risk = row["risk_level"]

        if risk == "high":
            high_risk += 1

        elif risk == "medium":
            medium_risk += 1

        elif risk == "low":
            low_risk += 1

    return {
        "total_regions": total_regions,
        "high_risk_regions": high_risk,
        "medium_risk_regions": medium_risk,
        "low_risk_regions": low_risk
    }