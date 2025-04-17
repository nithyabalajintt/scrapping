from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import string
import random

# Configure Selenium options
chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Start WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Base URLs
base_url = "https://www.moneycontrol.com/india/stockpricequote/"
all_urls = [f"{base_url}{letter}" for letter in string.ascii_uppercase] + [f"{base_url}others"]

company_names = set()

# XPaths to Try
xpaths = [
    '//table//tr/td[2]/a',
    '//div[@class="company_list"]//a'
]

# Scrape Each Page (A-Z + Others)
for url in all_urls:
    print(f"🔄 Scraping: {url}")

    for attempt in range(3):  # Retry 3 times if needed
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Try different XPaths
            for xpath in xpaths:
                elements = driver.find_elements(By.XPATH, xpath)
                if elements:
                    for element in elements:
                        name = element.text.strip()
                        if name:
                            company_names.add(name)
                    break  # Stop checking XPaths once data is found
            
            break  # Exit retry loop if successful
        except:
            print(f"⚠️ Retry {attempt + 1}/3 for {url}")
            time.sleep(5)
    
    # Random delay to prevent blocking
    time.sleep(random.uniform(3, 7))

driver.quit()

# Save to CSV
csv_filename = "company_names_A_Z_Others.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Company Name"])
    for name in sorted(company_names):
        writer.writerow([name])

print(f"✅ Extracted {len(company_names)} company names and saved to {csv_filename}")
