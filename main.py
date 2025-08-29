from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import time
import os

NAUKRI_EMAIL = os.environ.get("NAUKRI_EMAIL")
NAUKRI_PASSWORD = os.environ.get("NAUKRI_PASSWORD")

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.naukri.com/mnjuser/profile?id=&altresid")
driver.maximize_window()
driver.implicitly_wait(5)

driver.find_element(By.ID, "usernameField").send_keys(NAUKRI_EMAIL)
driver.find_element(By.ID, "passwordField").send_keys(NAUKRI_PASSWORD)
driver.find_element(By.XPATH, "//*[@id='loginForm']/div[2]/div[3]/div/button[1]").click()
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//*[@id='portal']/div/div[2]/div/img"))
).click()
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//div[@class='nI-gNb-drawer']"))
).click()
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='View & Update Profile']"))
).click()

RESUME_PATH = os.environ.get("RESUME_PATH", "Bhuvan_Resume.pdf")
file_path = os.path.join(os.getcwd(), RESUME_PATH)
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")


uploadInput = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file'].upload-input"))
)
driver.execute_script("arguments[0].style.display = 'block';", uploadInput)  # unhide if hidden
uploadInput.send_keys(file_path)

print("Resume uploaded")
driver.quit()