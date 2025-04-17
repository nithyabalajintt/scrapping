from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import string
import random
from urllib.parse import urlparse

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

company_data = []

# XPath to Extract Company Links
xpath = '//table//tr/td[2]/a'

# Scrape Each Page (A-Z + Others)
for url in all_urls:
    print(f"🔄 Scraping: {url}")

    for attempt in range(3):  # Retry 3 times if needed
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            elements = driver.find_elements(By.XPATH, xpath)
            for element in elements:
                company_name = element.text.strip()
                company_url = element.get_attribute("href")

                if company_name and company_url:
                    # Extract Scrip Name from URL
                    scrip_name = urlparse(company_url).path.split("/")[-1]
                    company_data.append((company_name, scrip_name, company_url))
            
            break  # Exit retry loop if successful
        except:
            print(f"⚠️ Retry {attempt + 1}/3 for {url}")
            time.sleep(5)
    
    # Random delay to prevent blocking
    time.sleep(random.uniform(3, 7))

driver.quit()

# Save to CSV
csv_filename = "company_scrip_mapping.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Company Name", "Scrip Name", "URL"])
    for name, scrip, url in sorted(company_data):
        writer.writerow([name, scrip, url])

print(f"✅ Extracted {len(company_data)} companies with scrip names and saved to {csv_filename}")
