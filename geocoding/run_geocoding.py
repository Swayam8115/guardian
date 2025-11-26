from database.db import SessionLocal
from database.crud import get_rows_missing_coordinates, update_coordinates
from geocoding.geocoder import get_formatted_address, get_lat_lon
import time

def run_geo_code():
    db = SessionLocal()

    rows = get_rows_missing_coordinates(db)

    for row in rows:
        print("loop started")
        addr = get_formatted_address(row.location)
        lat, lon = get_lat_lon(addr,row.generalised_location)
        if lat and lon:
            update_coordinates(db, row.file_name, lat, lon)
        time.sleep(1.2)

    db.close()
