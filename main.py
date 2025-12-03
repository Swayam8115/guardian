from automations.process_fir import process_all_firs
from geocoding.run_geocoding import run_geo_code

def main():
    process_all_firs()
    run_geo_code()

if __name__ == "__main__":
    main()