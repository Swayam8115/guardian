from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os, time

# -------------------------------------
# CONFIG
# -------------------------------------
FROM_DATE = "01/07/2025"
TO_DATE   = "31/07/2025"

DISTRICT_NAME = "BEED"        # <-- THIS IS "Unit*"
POLICE_STATION = None         # auto-select if None

DOWNLOAD_DIR = r"C:\Web_Scraping\FIRs"
CHROMEDRIVER_PATH = r"C:\WebDriver\chromedriver.exe"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

options = Options()
options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_DIR,
    "plugins.always_open_pdf_externally": True
})

# FIX WINDOW SIZE (Desktop)
options.add_argument("--window-size=1920,1080")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
wait = WebDriverWait(driver, 30)

driver.get("https://citizen.mahapolice.gov.in/Citizen/MH/PublishedFIRs.aspx")
time.sleep(3)

# 🔄 AUTO-REFRESH PAGE ONCE AFTER LOAD
driver.refresh()
time.sleep(3)

# -------------------------------------
# SET DATES
# -------------------------------------
driver.execute_script(
    "document.getElementById('ContentPlaceHolder1_txtDateOfRegistrationFrom').value = arguments[0]",
    FROM_DATE
)
driver.execute_script(
    "document.getElementById('ContentPlaceHolder1_txtDateOfRegistrationTo').value = arguments[0]",
    TO_DATE
)
time.sleep(2)

# -------------------------------------
# SELECT DISTRICT  (this is Unit*)
# -------------------------------------
district_dropdown = wait.until(
    EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlDistrict"))
)
sel_dist = Select(district_dropdown)

print("DISTRICT OPTIONS:", [o.text for o in sel_dist.options])

found = False
for opt in sel_dist.options:
    if DISTRICT_NAME.upper() in opt.text.upper():
        opt.click()
        #print("Selected District:", opt.text)
        found = True
        break

if not found:
    print("District NOT found:", DISTRICT_NAME)
    driver.quit()
    exit()

time.sleep(3)

# -------------------------------------
# SELECT POLICE STATION
# -------------------------------------
ps_dropdown = wait.until(
    EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlPoliceStation"))
)
sel_ps = Select(ps_dropdown)

print("POLICE STATION OPTIONS:", [o.text for o in sel_ps.options])

if POLICE_STATION:
    for opt in sel_ps.options:
        if POLICE_STATION.upper() in opt.text.upper():
            opt.click()
            print("Selected Police Station:", opt.text)
            break
else:
    if len(sel_ps.options) > 1:
        sel_ps.options[1].click()
        print("Auto-selected Police Station:", sel_ps.options[1].text)

time.sleep(2)

# -------------------------------------
# CLICK SEARCH
# -------------------------------------
search_btn = wait.until(EC.element_to_be_clickable((By.ID, "ContentPlaceHolder1_btnSearch")))
driver.execute_script("arguments[0].click();", search_btn)
time.sleep(4)

# -------------------------------------
# DOWNLOAD FIRs
# -------------------------------------
def download_firs():
    btns = driver.find_elements(By.XPATH, "//input[@value='Download']")
    print("Found", len(btns), "FIRs")
    for i, b in enumerate(btns, 1):
        driver.execute_script("arguments[0].click();", b)
        print("Downloaded FIR", i)
        time.sleep(1.5)

download_firs()

# PAGINATION
while True:
    try:
        next_btn = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Next")))
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(3)
        download_firs()
    except:
        print("No more pages.")
        break

driver.quit()
print("All FIRs downloaded successfully.")
