import os
import time
import random
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
logging.basicConfig(level=logging.INFO, filename='scraper.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load company identifiers
input_file = "company_identifier.csv"
df = pd.read_csv(input_file).head(2)

# Setup WebDriver options
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920x1080")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL templates
url_patterns = {
    "Balance Sheet": "https://www.moneycontrol.com/financials/{identifier}/balance-sheetVI/{scrip}#{scrip}",
    "Profit & Loss": "https://www.moneycontrol.com/financials/{identifier}/profit-lossVI/{scrip}#{scrip}",
    "Yearly Results": "https://www.moneycontrol.com/financials/{identifier}/results/yearly/{scrip}#{scrip}",
    "Cash Flow": "https://www.moneycontrol.com/financials/{identifier}/cash-flowVI/{scrip}#{scrip}",
    "Ratios": "https://www.moneycontrol.com/financials/{identifier}/ratiosVI/{scrip}#{scrip}",
    "Capital Structure": "https://www.moneycontrol.com/financials/{identifier}/capital-structure/{scrip}#{scrip}"
}

# Create output folder
output_dir = "financial_data"
os.makedirs(output_dir, exist_ok=True)

# Utility: Try closing cookie consent/pop-ups
def close_popups():
    try:
        # Cookie or privacy banner
        buttons = driver.find_elements(By.TAG_NAME, "button") + driver.find_elements(By.TAG_NAME, "a")
        for btn in buttons:
            text = btn.text.strip().lower()
            if any(t in text for t in ["accept", "agree", "close", "×", "no thanks"]):
                try:
                    btn.click()
                    logging.info("Closed a pop-up or cookie banner.")
                    time.sleep(1)
                    break
                except:
                    continue
    except Exception as e:
        logging.warning(f"Could not close pop-up: {e}")

# Start scraping
for index, row in df.iterrows():
    identifier = str(row.get('Identifier', '')).strip()
    scrip = str(row.get('Scrip Name', '')).strip()
    company_name = str(row.get('Company Name', '')).replace(" ", "_").strip()
    output_file = os.path.join(output_dir, f"{company_name}.xlsx")

    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        for section, url_template in url_patterns.items():
            url = url_template.format(identifier=identifier, scrip=scrip)
            logging.info(f"Scraping {section} for: {company_name} ({scrip})")
            driver.get(url)

            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                # Try closing popups
                close_popups()

                # Check for "Consolidated" tab
                try:
                    consolidated_tab = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Consolidated')]"))
                    )
                    consolidated_tab.click()
                    time.sleep(2)
                except:
                    logging.info(f"No Consolidated data for {company_name}, using Standalone.")

                # Locate table
                table_xpath = "//div[@id='new-format']//table[contains(@class, 'mctable1')]"
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, table_xpath)))
                table = driver.find_element(By.XPATH, table_xpath)
                rows = table.find_elements(By.TAG_NAME, "tr")

                if len(rows) < 2:
                    logging.warning(f"{section} table for {company_name} is empty.")
                    continue

                # Extract headers and data
                headers = [col.text.strip() for col in rows[0].find_elements(By.TAG_NAME, "td")]
                data = [[col.text.strip() for col in row.find_elements(By.TAG_NAME, "td")] for row in rows[1:]]

                df_section = pd.DataFrame(data, columns=headers if headers else None)
                df_section.to_excel(writer, sheet_name=section[:31], index=False)

                logging.info(f"Saved {section} for {company_name}")

            except Exception as e:
                logging.error(f"Failed to scrape {section} for {company_name}: {e}")

            time.sleep(random.uniform(2, 4))

driver.quit()
print("Scraping completed.")
