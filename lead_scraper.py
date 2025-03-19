from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Configure Selenium with ChromeDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  
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
            element.click()
            time.sleep(3)
            
            # Extracting business details
            business_location = "N/A"
            business_phone = "N/A"
            business_website = "N/A"
            business_email = "N/A"
            
            try:
                location_element = driver.find_element(By.CLASS_NAME, "Io6YTe")
                business_location = location_element.text
            except:
                pass
            
            try:
                details = driver.find_elements(By.CLASS_NAME, "UsdlK")
                for detail in details:
                    text = detail.text
                    if "@" in text:
                        business_email = text
                    elif text.startswith("http"):
                        business_website = text
                    elif text.replace(" ", "").isdigit():
                        business_phone = text
            except:
                pass
            
            business_info = {
                "nom": business_name,
                "num": business_phone,
                "web": business_website,
                "ubi": business_location,
                "email": business_email
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
