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

# Add user-agent to mimic real browser and avoid detection
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
)

# Additional anti-detection measures
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Detect Chromium binary
chromium_path = shutil.which("chromium-browser") or shutil.which("chromium") or shutil.which("google-chrome")
if chromium_path:
    chrome_options.binary_location = chromium_path

# Detect chromedriver
chromedriver_path = shutil.which("chromedriver")
if chromedriver_path:
    print(f"Using chromedriver at: {chromedriver_path}")

# Create service for chromedriver
from selenium.webdriver.chrome.service import Service
service = Service(chromedriver_path) if chromedriver_path else None
driver = webdriver.Chrome(service=service, options=chrome_options)

# Remove webdriver properties to avoid detection
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# Start with the main Naukri page first
driver.get("https://www.naukri.com")
driver.maximize_window()
driver.implicitly_wait(10)

# Wait for page to load and check if we need to login
wait = WebDriverWait(driver, 20)
print("Page loaded, checking for login form...")
print(f"Current URL: {driver.current_url}")
print(f"Page title: {driver.title}")

try:
    # First, let's check if we're already logged in by looking for profile elements
    try:
        profile_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'View & Update Profile')]")))
        print("Already logged in, proceeding to profile...")
        profile_link.click()
    except TimeoutException:
        print("Profile link not found, checking for login form...")
        
        # Try to find login form - check multiple possible locations
        username_field = None
        try:
            username_field = wait.until(EC.presence_of_element_located((By.ID, "usernameField")))
            print("Login form found by ID 'usernameField'")
        except TimeoutException:
            try:
                username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
                print("Login form found by NAME 'username'")
            except TimeoutException:
                try:
                    username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
                    print("Login form found by CSS selector 'input[type=email]'")
                except TimeoutException:
                    print("No login form found with any selector")
                    # Save screenshot and page source for debugging
                    driver.save_screenshot("no_login_form.png")
                    print("Saved screenshot: no_login_form.png")
                    print("Page source preview:")
                    print(driver.page_source[:2000])
                    raise Exception("Could not find login form with any selector")
        
        print("Login form found, attempting to login...")
        
        username_field.send_keys(NAUKRI_EMAIL)
        
        # Find password field
        password_field = None
        try:
            password_field = driver.find_element(By.ID, "passwordField")
        except NoSuchElementException:
            try:
                password_field = driver.find_element(By.NAME, "password")
            except NoSuchElementException:
                password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        
        password_field.send_keys(NAUKRI_PASSWORD)
        
        # Try different login button selectors
        login_button = None
        try:
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        except NoSuchElementException:
            try:
                login_button = driver.find_element(By.XPATH, "//*[@id='loginForm']//button")
            except NoSuchElementException:
                try:
                    login_button = driver.find_element(By.XPATH, "//button[contains(text(),'Login')]")
                except NoSuchElementException:
                    login_button = driver.find_element(By.XPATH, "//button[contains(text(),'Sign In')]")
        
        print(f"Found login button: {login_button.text}")
        login_button.click()
        print("Login button clicked, waiting for redirect...")
        
        # Wait for login to complete and page to load
        print("Waiting for login to complete...")
        time.sleep(8)  # Increased wait time
        
        # Now try to find the profile link
        profile_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'View & Update Profile')]")))
        profile_link.click()
        print("Profile link clicked successfully")
        
        # Wait a bit for the profile page to load
        time.sleep(3)
        
        # If we're not on the profile page yet, navigate directly
        if "profile" not in driver.current_url.lower():
            print("Navigating directly to profile page...")
            driver.get("https://www.naukri.com/mnjuser/profile?id=&altresid")
            time.sleep(3)
        
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

# Resume upload section
try:
    RESUME_PATH = os.environ.get("RESUME_PATH", "Bhuvan_Resume.pdf")
    file_path = os.path.join(os.getcwd(), RESUME_PATH)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found: {file_path}")
    
    print(f"Attempting to upload resume: {file_path}")
    
    uploadInput = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file'].upload-input"))
    )
    driver.execute_script("arguments[0].style.display = 'block';", uploadInput)
    uploadInput.send_keys(file_path)
    
    print("Resume uploaded successfully")
    
except Exception as e:
    print(f"Error during resume upload: {e}")
    driver.save_screenshot("upload_error.png")
    print("Saved upload error screenshot: upload_error.png")
    raise
finally:
    driver.quit()
