from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os, shutil, time

NAUKRI_EMAIL = os.environ.get("NAUKRI_EMAIL")
NAUKRI_PASSWORD = os.environ.get("NAUKRI_PASSWORD")

chrome_options = webdriver.ChromeOptions()

# Detect if running in GitHub Actions
if os.environ.get("GITHUB_ACTIONS") == "true":
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

# Detect Chromium binary
chromium_path = shutil.which("chromium-browser") or shutil.which("chromium") or shutil.which("google-chrome")
if chromium_path:
    chrome_options.binary_location = chromium_path

# Detect chromedriver
chromedriver_path = shutil.which("chromedriver")
if chromedriver_path:
    print(f"Using chromedriver at: {chromedriver_path}")

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://www.naukri.com/mnjuser/profile?id=&altresid")
driver.maximize_window()
driver.implicitly_wait(10)

# Wait for page to load and check if we need to login
wait = WebDriverWait(driver, 20)
print("Page loaded, checking for login form...")

try:
    # First, let's check if we're already logged in by looking for profile elements
    try:
        profile_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'View & Update Profile')]")))
        print("Already logged in, proceeding to profile...")
        profile_link.click()
    except TimeoutException:
        print("Profile link not found, checking for login form...")
        
        # Try to find login form
        username_field = wait.until(EC.presence_of_element_located((By.ID, "usernameField")))
        print("Login form found, attempting to login...")
        
        username_field.send_keys(NAUKRI_EMAIL)
        password_field = driver.find_element(By.ID, "passwordField")
        password_field.send_keys(NAUKRI_PASSWORD)
        
        # Try different login button selectors
        try:
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        except NoSuchElementException:
            try:
                login_button = driver.find_element(By.XPATH, "//*[@id='loginForm']//button")
            except NoSuchElementException:
                login_button = driver.find_element(By.XPATH, "//button[contains(text(),'Login')]")
        
        login_button.click()
        print("Login button clicked, waiting for redirect...")
        
        # Wait for login to complete
        time.sleep(5)
        
        # Now try to find the profile link
        profile_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'View & Update Profile')]")))
        profile_link.click()
        print("Profile link clicked successfully")
        
except Exception as e:
    print(f"Error during login process: {e}")
    print("Current page title:", driver.title)
    print("Current URL:", driver.current_url)
    
    # Save screenshot for debugging
    driver.save_screenshot("error_page.png")
    print("Saved error screenshot: error_page.png")
    
    # Try to get page source for debugging
    print("Page source preview:")
    print(driver.page_source[:1000])
    
    raise

RESUME_PATH = os.environ.get("RESUME_PATH", "Bhuvan_Resume.pdf")
file_path = os.path.join(os.getcwd(), RESUME_PATH)

uploadInput = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file'].upload-input"))
)
driver.execute_script("arguments[0].style.display = 'block';", uploadInput)
uploadInput.send_keys(file_path)

print("Resume uploaded successfully")
driver.quit()
