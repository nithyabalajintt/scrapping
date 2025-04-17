import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load company identifiers
input_file = "company_identifier.csv"
df = pd.read_csv(input_file).head(2)  # Process first 2 companies

# Setup WebDriver with headless mode
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Base URL formats for different financial details
url_patterns = {
    "Balance Sheet": "https://www.moneycontrol.com/financials/{identifier}/balance-sheetVI/{scrip}#{scrip}",
    "Profit & Loss": "https://www.moneycontrol.com/financials/{identifier}/profit-lossVI/{scrip}#{scrip}",
    "Yearly Results": "https://www.moneycontrol.com/financials/{identifier}/results/yearly/{scrip}#{scrip}",
    "Cash Flow": "https://www.moneycontrol.com/financials/{identifier}/cash-flowVI/{scrip}#{scrip}",
    "Ratios": "https://www.moneycontrol.com/financials/{identifier}/ratiosVI/{scrip}#{scrip}",
    "Capital Structure": "https://www.moneycontrol.com/financials/{identifier}/capital-structure/{scrip}#{scrip}"
}

# Directory to save files
output_dir = "financial_data"
os.makedirs(output_dir, exist_ok=True)

for index, row in df.iterrows():
    identifier = row['Identifier']  # Ensure correct column name
    scrip = row['Scrip Name']  # Corrected column name
    company_name = row['Company Name'].replace(" ", "_")  # Sanitize filename
    output_file = os.path.join(output_dir, f"{company_name}.xlsx")
    
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        for section, url_template in url_patterns.items():
            url = url_template.format(identifier=identifier, scrip=scrip)
            print(f"Scraping {section} for: {company_name} ({scrip})")
            driver.get(url)
            
            try:
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Wait for the financial table
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='new-format']//table[contains(@class, 'mctable1')]")
                ))
                
                # Extract Table
                table = driver.find_element(By.XPATH, "//div[@id='new-format']//table[contains(@class, 'mctable1')]")
                rows = table.find_elements(By.TAG_NAME, "tr")
                
                data = []
                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    data.append([col.text.strip() for col in cols])
                
                # Convert to DataFrame
                df_section = pd.DataFrame(data)
                df_section.to_excel(writer, sheet_name=section, index=False, header=False)
                print(f"Saved {section} for {company_name}")
                
            except Exception as e:
                print(f"Failed to scrape {section} for {company_name}: {e}")
            
            time.sleep(3)  # To avoid getting blocked

driver.quit()
