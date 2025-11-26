from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import time
import shutil

# -------------------------------------
# CONFIG
# -------------------------------------
FROM_DATE = "01/10/2025"
TO_DATE   = "31/10/2025"

DISTRICT_NAME = "PUNE CITY"     # EXACT text as in dropdown
BASE_DOWNLOAD_DIR = r"E:\FIR"   # Root download directory

os.makedirs(BASE_DOWNLOAD_DIR, exist_ok=True)

options = Options()
# options.add_experimental_option("prefs", {
#     "download.default_directory": BASE_DOWNLOAD_DIR,
#     "plugins.always_open_pdf_externally": True
# })
options.add_experimental_option("prefs", {
    "download.default_directory": BASE_DOWNLOAD_DIR,
    "plugins.always_open_pdf_externally": True,
    "profile.default_content_setting_values.automatic_downloads": 1,  # allow multiple downloads
    "profile.default_content_settings.popups": 0                     # disable popups
})


options.add_argument("--window-size=1920,1080")
options.add_argument("--start-maximized")


driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)

driver.get("https://citizen.mahapolice.gov.in/Citizen/MH/PublishedFIRs.aspx")
time.sleep(3)
driver.refresh()
time.sleep(3)


# -------------------------------------
# HELPERS
# -------------------------------------
def sanitize_folder_name(name):
    bad = '<>:"/\\|?*'
    for c in bad:
        name = name.replace(c, "_")
    return name.strip()


def set_dates():
    driver.execute_script(
        "document.getElementById('ContentPlaceHolder1_txtDateOfRegistrationFrom').value = arguments[0]",
        FROM_DATE
    )
    driver.execute_script(
        "document.getElementById('ContentPlaceHolder1_txtDateOfRegistrationTo').value = arguments[0]",
        TO_DATE
    )
    time.sleep(1)


def set_view_record_to_50():
    """Try to set 'View Record' to 50"""
    try:
        dropdown = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//select[contains(@id,'ddlPageSize') or contains(@id,'ddlPage')]"
            ))
        )
        Select(dropdown).select_by_visible_text("50")
        time.sleep(3)
        print("  View Record set to 50")
    except:
        print("  Could not set View Record (not found)")


def download_firs_on_page():
    buttons = driver.find_elements(By.XPATH, "//input[@value='Download']")
    print("  Found", len(buttons), "FIRs on this page")
    for i, b in enumerate(buttons, start=1):
        try:
            driver.execute_script("arguments[0].click();", b)
            print(f"    Downloaded FIR {i}")
            time.sleep(1.5)
        except Exception as e:
            print("    Error:", e)


def download_all_pages_for_current_filters():
    """Click page numbers 1..N and download FIRs from each."""
    time.sleep(3)

    pager_elems = driver.find_elements(
        By.XPATH,
        "//tr[contains(@class,'GridPager')]//td//a | "
        "//tr[contains(@class,'GridPager')]//td//span"
    )

    if not pager_elems:
        print("  Single page only")
        download_firs_on_page()
        return

    page_nums = []
    for el in pager_elems:
        t = el.text.strip()
        if t.isdigit():
            page_nums.append(int(t))

    if not page_nums:
        print("  Single page only")
        download_firs_on_page()
        return

    max_page = max(page_nums)
    print("  Total pages =", max_page)

    for page in range(1, max_page + 1):
        if page > 1:
            try:
                link = wait.until(
                    EC.element_to_be_clickable((By.LINK_TEXT, str(page)))
                )
                driver.execute_script("arguments[0].click();", link)
                time.sleep(2)
            except Exception as e:
                print(f"  Failed to open page {page}", e)
                break

        print(f"  >>> Page {page}")
        download_firs_on_page()


def process_police_station(ps_name):
    print(f"\n=== Processing Police Station: {ps_name} ===")

    folder = sanitize_folder_name(ps_name)
    ps_dir = os.path.join(BASE_DOWNLOAD_DIR, folder)
    os.makedirs(ps_dir, exist_ok=True)

    before = {f for f in os.listdir(BASE_DOWNLOAD_DIR) if f.lower().endswith(".pdf")}

    # Reselect district (stale fix)
    district_dropdown = wait.until(
        EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlDistrict"))
    )
    sel_dist = Select(district_dropdown)

    for opt in sel_dist.options:
        if DISTRICT_NAME.upper() in opt.text.upper():
            label = opt.text      # read BEFORE click
            opt.click()
            print("  District selected:", label)
            break
    time.sleep(1)

    # Select police station
    ps_dropdown = wait.until(
        EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlPoliceStation"))
    )
    sel_ps = Select(ps_dropdown)
    sel_ps.select_by_visible_text(ps_name)
    print("  Police Station selected:", ps_name)
    time.sleep(1)

    # Set dates & Search
    set_dates()
    search_btn = wait.until(
        EC.element_to_be_clickable((By.ID, "ContentPlaceHolder1_btnSearch"))
    )
    driver.execute_script("arguments[0].click();", search_btn)
    time.sleep(4)

    # Set View Record
    set_view_record_to_50()

    # Download all pages
    download_all_pages_for_current_filters()

    # Move new files
    after = {f for f in os.listdir(BASE_DOWNLOAD_DIR) if f.lower().endswith(".pdf")}
    new_files = after - before

    if not new_files:
        print("  No new FIRs found.\n")
        return

    for f in new_files:
        try:
            shutil.move(os.path.join(BASE_DOWNLOAD_DIR, f), os.path.join(ps_dir, f))
            print("  Moved:", f)
        except Exception as e:
            print("  Error moving file:", e)


# -------------------------------------
# MAIN FLOW
# -------------------------------------
set_dates()

district_dropdown = wait.until(
    EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlDistrict"))
)
sel_dist = Select(district_dropdown)

print("DISTRICT OPTIONS:", [o.text for o in sel_dist.options])

# Select district once at start (stale-safe)
for opt in sel_dist.options:
    if DISTRICT_NAME.upper() in opt.text.upper():
        label = opt.text
        opt.click()
        print("Selected District:", label)
        break

time.sleep(3)

# Load police stations
ps_dropdown = wait.until(
    EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlPoliceStation"))
)
sel_ps = Select(ps_dropdown)

all_ps = [
    o.text for o in sel_ps.options
    if o.text.strip().upper() != "SELECT"
]

print("POLICE STATIONS:", all_ps)

# PROCESS EACH POLICE STATION
for ps_name in all_ps:
    process_police_station(ps_name)

driver.quit()
print("\nAll FIRs downloaded successfully.")