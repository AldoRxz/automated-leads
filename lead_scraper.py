from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

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
            business_info = {
                "nom": business_name,
                "num": "N/A",  
                "web": "N/A",  
                "ubi": "N/A",  
                "email": "N/A"  
            }
            businesses.append(business_info)
        except:
            continue
    
    return businesses


# Example 
search_name = "taller mecanico"
search_location = "CDMX"
results = search_businesses(search_name, search_location)

# Print results
for business in results:
    print(business)

driver.quit()
