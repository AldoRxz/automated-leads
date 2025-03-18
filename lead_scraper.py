from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

# Configure Selenium with ChromeDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in background
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)


# Function to search for businesses on Google Maps
def search_businesses(name, location):
    url = f"https://www.google.com/maps/search/{name}+{location}"
    driver.get(url)
    time.sleep(5)  
    
    businesses = []
    elements = driver.find_elements(By.CLASS_NAME, "Nv2PK")
    
    for element in elements:
        try:
            business_name = element.find_element(By.CLASS_NAME, "qBF1Pd").text
            businesses.append(business_name)
        except:
            continue
    
    return businesses


# Example 
search_name = "mechanic shop"
search_location = "CDMX"
results = search_businesses(search_name, search_location)

# Save to Excel
df = pd.DataFrame(results, columns=["Businesses"])
df.to_excel("businesses.xlsx", index=False)

print("Businesses saved in businesses.xlsx")

driver.quit()
