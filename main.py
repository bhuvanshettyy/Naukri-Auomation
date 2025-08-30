from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time, os, shutil

# Credentials from GitHub Secrets
NAUKRI_EMAIL = os.environ.get("NAUKRI_EMAIL")
NAUKRI_PASSWORD = os.environ.get("NAUKRI_PASSWORD")
RESUME_PATH = os.environ.get("RESUME_PATH", "Bhuvan_Resume.pdf")

# Configure Chrome options for GitHub Actions
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

# Detect chromium binary
chromium_path = shutil.which("chromium-browser") or shutil.which("chromium")
if chromium_path:
    print(f"Using chromium at: {chromium_path}")
    chrome_options.binary_location = chromium_path
else:
    raise FileNotFoundError("Chromium not found in runner")

# Detect chromedriver
chromedriver_path = shutil.which("chromedriver")
if not chromedriver_path:
    raise FileNotFoundError("Chromedriver not found in runner")
print(f"Using chromedriver at: {chromedriver_path}")

driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get("https://www.naukri.com/nlogin/login")
    wait = WebDriverWait(driver, 20)

    # Wait for email field
    email_field = wait.until(EC.presence_of_element_located((By.ID, "usernameField")))
    email_field.send_keys(NAUKRI_EMAIL)

    # Password
    driver.find_element(By.ID, "passwordField").send_keys(NAUKRI_PASSWORD)

    # Login button
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Wait for profile link after login
    profile_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'View & Update Profile')]")))
    profile_link.click()

    # Resume upload
    file_path = os.path.join(os.getcwd(), RESUME_PATH)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    upload_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file'].upload-input")))
    driver.execute_script("arguments[0].style.display = 'block';", upload_input)
    upload_input.send_keys(file_path)

    print("Resume uploaded successfully.")

except TimeoutException as e:
    print("Timeout occurred:", e)
    driver.save_screenshot("page.png")
    print("Saved screenshot: page.png")
    raise

finally:
    driver.quit()
