import os
import time
from datetime import datetime
import googlemaps
import gspread
from pprint import pprint
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials


env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path=env_path)
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not API_KEY:
    raise ValueError("❌ No se encontró la API KEY. Verifica el archivo .env o su ruta.")


gmaps = googlemaps.Client(key=API_KEY)


def buscar_negocios(nombre, ubicacion, max_resultados=10):
    resultados = []
    places_result = gmaps.places(query=f"{nombre} {ubicacion}")

    while places_result and len(resultados) < max_resultados:
        for lugar in places_result.get("results", []):
            info = {
                "Nombre": lugar.get("name"),
                "Dirección": lugar.get("formatted_address"),
                "Rating": lugar.get("rating", "N/A"),
                "Lugar_ID": lugar.get("place_id")
            }


            detalles = gmaps.place(place_id=info["Lugar_ID"]).get("result", {})
            info["Teléfono"] = detalles.get("formatted_phone_number", "N/A")
            info["Sitio Web"] = detalles.get("website", "N/A")
            info["Email"] = "N/A"  # No disponible vía API

            resultados.append(info)

            if len(resultados) >= max_resultados:
                break


        next_page_token = places_result.get("next_page_token")
        if next_page_token:
            print("⏳ Esperando que el next_page_token esté activo...")
            time.sleep(5)  # Espera recomendada
            try:
                places_result = gmaps.places(page_token=next_page_token)
            except googlemaps.exceptions.ApiError as e:
                print(f"⚠️ Error al obtener la siguiente página: {e}")
                break
        else:
            break

    return resultados


def conectar_google_sheets():
    cred_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'credenciales.json'))

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
    client = gspread.authorize(creds)
    return client


def guardar_en_sheets(negocios, nombre_busqueda):
    client = conectar_google_sheets()
    sheet_url = "https://docs.google.com/spreadsheets/d/1FyGDSrBsXsscmdiqiinDGfiJ1rIOfz_ybEa5AFsFmDc/edit"
    spreadsheet = client.open_by_url(sheet_url)


    fecha = datetime.now().strftime("%Y-%m-%d")
    nombre_hoja = f"{nombre_busqueda.capitalize()} - {fecha}"


    try:
        sheet = spreadsheet.worksheet(nombre_hoja)
        print(f"📄 La hoja '{nombre_hoja}' ya existe. Se sobrescribirá su contenido.")
        sheet.clear()  # Limpia contenido previo
    except gspread.exceptions.WorksheetNotFound:
        print(f"📄 Creando nueva hoja: {nombre_hoja}")
        sheet = spreadsheet.add_worksheet(title=nombre_hoja, rows="100", cols="10")


    sheet.update('A1', [[f"Resultados para: {nombre_busqueda.capitalize()}"]])


    encabezados = ["Nombre", "Teléfono", "Sitio Web", "Dirección", "Email"]
    sheet.append_row(encabezados, table_range='A2')


    for negocio in negocios:
        fila = [
            negocio.get("Nombre", ""),
            negocio.get("Teléfono", ""),
            negocio.get("Sitio Web", ""),
            negocio.get("Dirección", ""),
            negocio.get("Email", "")
        ]
        sheet.append_row(fila)

    print(f"✅ ¡Datos escritos en la hoja: {nombre_hoja}!")



if __name__ == "__main__":
    nombre_busqueda = "inmobiliaria"
    ubicacion_busqueda = "CDMX"
    max_resultados = 10

    print(f"🔍 Buscando '{nombre_busqueda}' en '{ubicacion_busqueda}'...")
    negocios = buscar_negocios(nombre_busqueda, ubicacion_busqueda, max_resultados)

    print("✅ Resultados encontrados:")
    pprint(negocios)

    print("📤 Guardando en Google Sheets...")
    guardar_en_sheets(negocios, nombre_busqueda)
