from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

# Configurar Selenium con ChromeDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Ejecutar en segundo plano
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Inicializar el driver
driver = webdriver.Chrome(options=options)

# Función para buscar negocios en Google Maps
def buscar_negocios(nombre, ubicacion, max_resultados=10):
    url = f"https://www.google.com/maps/search/{nombre}+{ubicacion}"
    driver.get(url)

    # Esperar a que carguen los resultados
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK"))
    )

    negocios = []
    elementos = driver.find_elements(By.CLASS_NAME, "Nv2PK")

    # Desplazarse para cargar más resultados
    for _ in range(5):  # Ajusta según necesidad
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(2)  # Esperar carga de nuevos elementos

    elementos = driver.find_elements(By.CLASS_NAME, "Nv2PK")[:max_resultados]

    for elemento in elementos:
        try:
            nombre_negocio = elemento.find_element(By.CLASS_NAME, "qBF1Pd").text
            elemento.click()
            time.sleep(3)

            # Extraer detalles
            direccion = "N/A"
            telefono = "N/A"
            web = "N/A"
            email = "N/A"

            try:
                direccion = driver.find_element(By.CLASS_NAME, "Io6YTe").text
            except:
                pass

            # Buscar teléfono, web y email en la lista de detalles
            detalles = driver.find_elements(By.CLASS_NAME, "UsdlK")
            for detalle in detalles:
                texto = detalle.text
                if "@" in texto:
                    email = texto
                elif texto.startswith("http"):
                    web = texto
                elif texto.replace(" ", "").isdigit():
                    telefono = texto

            negocios.append({
                "Nombre": nombre_negocio,
                "Teléfono": telefono,
                "Sitio Web": web,
                "Dirección": direccion,
                "Email": email
            })
        except Exception as e:
            print(f"Error procesando un negocio: {e}")
            continue

    return negocios

# Ejemplo de búsqueda
nombre_busqueda = "inmobiliaria"
ubicacion_busqueda = "CDMX"
resultados = buscar_negocios(nombre_busqueda, ubicacion_busqueda, max_resultados=10)

# Imprimir resultados
for negocio in resultados:
    print(negocio)

# Cerrar navegador
driver.quit()
