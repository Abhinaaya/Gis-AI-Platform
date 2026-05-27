from fastapi import APIRouter
import geopandas as gpd
from shapely.geometry import Point
import json
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from sqlalchemy import text
router = APIRouter()

# ✅ Path goes up 3 levels: routes → app → backend → GIS-AI-Platform → data

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)

FILE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "ghydmc-area.geojson"
)

FLOOD_FILE = os.path.join(
    BASE_DIR,
    "data",
    "flood_points.geojson"
)

def load_flood_data():
    if not os.path.exists(FLOOD_FILE):
        raise FileNotFoundError(f"Flood GeoJSON not found at: {FLOOD_FILE}")
    flood_gdf = gpd.read_file(FLOOD_FILE)
    if flood_gdf.crs and flood_gdf.crs.to_epsg() != 4326:
        flood_gdf = flood_gdf.to_crs(epsg=4326)
    return flood_gdf


def load_geodata():
    if not os.path.exists(FILE_PATH):
        raise FileNotFoundError(f"GeoJSON file not found at: {FILE_PATH}")
    gdf = gpd.read_file(FILE_PATH)
    # ✅ Reproject to WGS84 (lat/lon) — required by Leaflet
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    return gdf


@router.get("/geo-data")
def get_geo_data():
    gdf = load_geodata()

    # ✅ Convert all non-geometry columns to string to handle Timestamps, NaT, etc.
    non_geom_cols = [c for c in gdf.columns if c != "geometry"]
    gdf[non_geom_cols] = gdf[non_geom_cols].astype(str)

    return json.loads(gdf.to_json())


@router.get("/nearby")
def nearby_locations(lat: float, lon: float):
    gdf = load_geodata()
    user_point = Point(lon, lat)
    nearby = []
    for _, row in gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        distance = geom.distance(user_point)
        if distance < 0.05:
            nearby.append({
                "name": row.get("name", "Unknown"),
                "distance": round(distance, 6)
            })
    return {"nearby_locations": nearby}


@router.get("/risk-check")
def risk_check(lat: float, lon: float):
    gdf = load_geodata()
    user_point = Point(lon, lat)
    results = []
    for _, row in gdf.iterrows():
        polygon = row.geometry
        if polygon is None or polygon.is_empty:
            continue
        if polygon.contains(user_point):
            results.append({
                "region": row.get("name", "Unknown"),
                "status": "INSIDE GHMC"
                 
            })
    if not results:
        return {"status": "OUTSIDE GHMC"}
    return {"results": results}


@router.get("/risk-summary")
def risk_summary(lat: float, lon: float):
    gdf = load_geodata()
    user_point = Point(lon, lat)
    for _, row in gdf.iterrows():
        polygon = row.geometry
        if polygon is None or polygon.is_empty:
            continue
        if polygon.contains(user_point):
            return {"summary": f"You are inside {row.get('name', 'GHMC Region')}"}
    return {"summary": "This location is outside GHMC."}


@router.get("/statistics")
def statistics():
    gdf = load_geodata()
    return {
        "total_regions": len(gdf),
        "columns": list(gdf.columns),
        "crs": str(gdf.crs)
    }


@router.get("/inside-ghmc")
def inside_ghmc(lat: float, lon: float):
    gdf = load_geodata()
    user_point = Point(lon, lat)
    for _, row in gdf.iterrows():
        polygon = row.geometry
        if polygon is None or polygon.is_empty:
            continue
        if polygon.contains(user_point):
            return {
                "status": "INSIDE GHMC",
                "region_name": row.get("name", "Unknown"),
                "risk_level": row.get("risk_level", "unknown")
            }
    return {"status": "OUTSIDE GHMC"}

@router.get("/flood-points")
def get_flood_points():

    db: Session = SessionLocal()

    query = text("""
        SELECT
            id,
            location_name,
            risk_level,
            ST_Y(geom) AS lat,
            ST_X(geom) AS lon
        FROM flood_points
    """)

    result = db.execute(query)

    points = []

    for row in result:
        points.append({
            "id": row.id,
            "location": row.location_name,
            "risk": row.risk_level,
            "lat": row.lat,
            "lon": row.lon
        })

    db.close()

    return points


@router.get("/flood-data")
def flood_data():
    flood_gdf = load_flood_data()
    non_geom_cols = [c for c in flood_gdf.columns if c != "geometry"]
    flood_gdf[non_geom_cols] = flood_gdf[non_geom_cols].astype(str)
    return json.loads(flood_gdf.to_json())


@router.get("/check-flood-risk")
def check_flood_risk(lat: float, lon: float):
    flood_gdf = load_flood_data()
    user_point = Point(lon, lat)
    nearest_distance = 999999.0
    nearest_name = "Unknown"
    for _, row in flood_gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        distance = geom.distance(user_point)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_name = (
                row.get("Name")
                or row.get("name")
                or row.get("unknown")
            )
    if nearest_distance < 0.01:
        risk = "HIGH"
    elif nearest_distance < 0.03:
        risk = "MEDIUM"
    else:
        risk = "LOW"
    return {
        "risk": risk,
        "nearest_flood_point": nearest_name,
        "distance": round(nearest_distance, 5)
    }


@router.get("/analyze-risk")
def analyze_risk(lat: float, lon: float):
    flood_gdf = load_flood_data()
    user_point = Point(lon, lat)
    min_distance = 999999.0
    nearest_location = "Unknown"
    for _, row in flood_gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        distance = user_point.distance(geom)
        if distance < min_distance:
            min_distance = distance
            nearest_location = (
                row.get("Name")
                or row.get("name")
                or row.get("unknown")
            )
    if min_distance < 0.01:
        risk = "HIGH"
    elif min_distance < 0.03:
        risk = "MEDIUM"
    else:
        risk = "LOW"
    return {
        "risk": risk,
        "nearest_flood_point": nearest_location,
        "distance": round(min_distance, 5)
    }
@router.get("/nearest-flood")
def nearest_flood(lat: float, lon: float):

    db: Session = SessionLocal()

    query = text("""
        SELECT
            id,
            location_name,
            risk_level,

            ST_Distance(
                geom::geography,
                ST_SetSRID(
                    ST_MakePoint(:lon, :lat),
                    4326
                )::geography
            ) AS distance

        FROM flood_points

        ORDER BY distance

        LIMIT 1
    """)

    result = db.execute(
        query,
        {
            "lat": lat,
            "lon": lon
        }
    )

    row = result.fetchone()

    db.close()

    return {
        "nearest_location": row.location_name,
        "risk_level": row.risk_level,
        "distance_meters": round(row.distance, 2)
    }

