import requests
from config.settings import settings
import time

CLIENT_ID = settings.MAPMYINDIA_CLIENT_ID
CLIENT_SECRET = settings.MAPMYINDIA_CLIENT_SECRET


def get_token():
    url = "https://outpost.mapmyindia.com/api/security/oauth/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    r = requests.post(url, data=data)
    return r.json().get("access_token")


def get_formatted_address(raw_address: str):
    token = "0b70c006-2d79-4d44-9c32-8f5a4a0ed6fb"
    url = "https://atlas.mapmyindia.com/api/places/geocode"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "address": raw_address,
        "region": "ind",
        "bias": 1,              
        "podFilter": "slc"
    }
    
    r = requests.get(url, headers=headers, params=params).json()
    cop = r.get("copResults", {})
    return cop.get("formattedAddress")


def osm_search(address: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "fir-geocoder/1.0 (contact: swaraj1432k4@gmail.com)"
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.text.startswith("<"):
            print("HTML response from OSM (rate limit / error)")
            return None
        text = resp.text.strip()
        if not text:
            return None
        return resp.json()
    except Exception:
        return None


def get_lat_lon(address: str,add1: str):
    
    result = osm_search(address)
    if not result:
        print("Using generalised Location")
        time.sleep(1.2)
        add2 = get_formatted_address(add1)
        result = osm_search(add2)
        if not result :
            print("Generalised location also failed")
            token = "0b70c006-2d79-4d44-9c32-8f5a4a0ed6fb"
            url = "https://atlas.mapmyindia.com/api/places/geocode"
            headers = {"Authorization": f"Bearer {token}"}
            params = {
                "address": add2,
                "region": "ind",
                "bias": 1,              
                "podFilter": "loc"
            }
            
            r = requests.get(url, headers=headers, params=params).json()
            cop = r.get("copResults", {})
            add3=cop.get("formattedAddress")
            result = osm_search(add3)
            if not result:
                print("SAB FAILED QUERY KI MKC")
                return None,None

    top = result[0]
    lat = float(top.get("lat"))
    lon = float(top.get("lon"))
    return lat, lon


