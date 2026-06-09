import time
import requests
from config.settings import settings
from database.db import SessionLocal
from database.crud import get_rows_missing_coordinates, update_coordinates

GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"


def get_lat_lon(address: str) -> tuple:
    params = {
        "address": address,
        "key": settings.GOOGLE_MAP_API_KEY,
    }
    try:
        response = requests.get(GEOCODING_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "OK":
            print(f"  [geocode] status={data.get('status')} for: {address}")
            return None, None
        location = data["results"][0]["geometry"]["location"]
        return float(location["lat"]), float(location["lng"])
    except Exception as e:
        print(f"  [geocode] error: {e}")
        return None, None


def run_geocoding():
    db = SessionLocal()
    try:
        rows = get_rows_missing_coordinates(db)
        print(f"Found {len(rows)} rows missing coordinates.")

        for row in rows:
            print(f"\nGeocoding: {row.location}")
            lat, lon = get_lat_lon(row.location)
            if lat is not None and lon is not None:
                update_coordinates(db, row.file_name, lat, lon)
                print(f"  Stored: lat={lat}, lon={lon}")
            else:
                print(f"  Failed to geocode, skipping.")
            time.sleep(0.2)
    finally:
        db.close()
