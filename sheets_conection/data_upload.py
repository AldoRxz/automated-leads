import os
import time
import gspread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Paths and Google Sheets setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")

gc = gspread.service_account(filename=CREDENTIALS_FILE)
SHEET_ID = "1ZBC1KSj44Tpm9Z5MAMudxxZtOEBbJLs_YMH-nbu3fNE"
spreadsheet = gc.open_by_key(SHEET_ID)
worksheet = spreadsheet.sheet1

# Selenium ChromeDriver config
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# Business search on Google Maps
def buscar_negocios(nombre, ubicacion, max_resultados=10):
    url = f"https://www.google.com/maps/search/{nombre}+{ubicacion}"
    driver.get(url)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK"))
    )

    negocios = []
    elementos = driver.find_elements(By.CLASS_NAME, "Nv2PK")

    # Scroll to load more results
    for _ in range(5):  
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(2)

    elementos = driver.find_elements(By.CLASS_NAME, "Nv2PK")[:max_resultados]

    for i, elemento in enumerate(elementos, start=1):
        try:
            nombre_negocio = elemento.find_element(By.CLASS_NAME, "qBF1Pd").text
            elemento.click()
            time.sleep(8)

            direccion = "N/A"
            telefono = "N/A"
            web = "N/A"
            email = "N/A"

            try:
                direccion = driver.find_element(By.CLASS_NAME, "Io6YTe").text
            except:
                pass

            # Try multiple ways to extract phone number
            try:
                telefono_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='tel:']"))
                )
                telefono = telefono_element.text.strip()
            except:
                try:
                    detalles = driver.find_elements(By.CLASS_NAME, "UsdlK")
                    for detalle in detalles:
                        texto = detalle.text.strip()
                        if "55" in texto and texto.replace(" ", "").replace("-", "").isdigit():
                            telefono = texto
                            break
                except:
                    pass

            if telefono == "N/A":
                try:
                    telefono_alt = driver.find_element(By.XPATH, "//span[contains(text(), '55') or contains(text(), '+')]").text.strip()
                    if "55" in telefono_alt and telefono_alt.replace(" ", "").replace("-", "").isdigit():
                        telefono = telefono_alt
                except:
                    pass

            if telefono == "N/A":
                try:
                    telefono_div = driver.find_element(By.XPATH, "//div[contains(text(), '55')]").text.strip()
                    if "55" in telefono_div and telefono_div.replace(" ", "").replace("-", "").isdigit():
                        telefono = telefono_div
                except:
                    pass

            if telefono == "N/A":
                try:
                    telefono_span = driver.find_element(By.XPATH, "//span[contains(@class, 'UsdlK')]").text.strip()
                    if "55" in telefono_span and telefono_span.replace(" ", "").replace("-", "").isdigit():
                        telefono = telefono_span
                except:
                    pass

            if telefono == "N/A":
                try:
                    telefono_final = driver.find_element(By.CLASS_NAME, "Io6YTe").text.strip()
                    if "55" in telefono_final and telefono_final.replace(" ", "").replace("-", "").isdigit():
                        telefono = telefono_final
                except:
                    pass

            if telefono == "N/A":
                print(f"⚠️ {nombre_negocio} has no phone listed.")

            # Extract website
            try:
                web_element = driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
                web = web_element.get_attribute("href")
            except:
                pass  

            print(f"📞 Found phone: {telefono} for {nombre_negocio}")

            negocios.append({
                "Nombre": nombre_negocio,
                "Teléfono": telefono,
                "Sitio Web": web,
                "Dirección": direccion,
                "Email": email
            })

        except Exception as e:
            print(f"❌ Error: {e}")
            continue

    return negocios

# Run search
nombre_busqueda = "inmobiliaria"
ubicacion_busqueda = "CDMX"
resultados = buscar_negocios(nombre_busqueda, ubicacion_busqueda, max_resultados=10)

# Upload to Google Sheets
if not worksheet.get_all_values():
    worksheet.append_row(["Nombre", "Teléfono", "Sitio Web", "Dirección", "Email"])

for negocio in resultados:
    worksheet.append_row([
        negocio["Nombre"],
        negocio["Teléfono"],
        negocio["Sitio Web"],
        negocio["Dirección"],
        negocio["Email"]
    ])

print("✅ Data uploaded to Google Sheets.")

# Close browser
driver.quit()
