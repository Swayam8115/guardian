from automations.process_fir import process_all_firs
from google_maps.geocodes import run_geocoding

def main():
    process_all_firs()
    run_geocoding()

if __name__ == "__main__":
    main()



    
