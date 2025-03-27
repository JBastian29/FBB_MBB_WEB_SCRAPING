import time
import requests
import csv
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# URLs

urls = {
        "JA": [
            "https://shop.digicelgroup.com/jm/devices/smartphones.html"
        ],
        "TT": [
            "https://shop.digicelgroup.com/devices/smartphones.html"
        ]
    }




def get_chromedriver_path():
    if getattr(sys, 'frozen', False):  # Si el script está empaquetado
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Ruta del chromedriver
    chromedriver_path = os.path.join(base_path, 'chromedriver.exe')
    return chromedriver_path


# Configuración de WebDriver (usando Chrome)
chromedriver_path = get_chromedriver_path()
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)


# Función para obtener los links de los productos en la página actual
def get_product_links():
    time.sleep(3)  # Esperar para asegurarse de que los elementos estén cargados
    product_links = []

    # Encontrar todos los artículos de productos
    product_elements = driver.find_elements(By.CLASS_NAME, "product-item-info")

    # Obtener los links de los productos
    for product in product_elements:
        link_element = product.find_element(By.TAG_NAME, "a")
        link = link_element.get_attribute("href")
        product_links.append(link)

    return product_links


# Función para obtener las especificaciones generales
def get_especificaciones_generales():
    try:
        # Esperar a que el nombre del producto esté visible
        product_name_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "page-title-wrapper"))
        )

        # Esperar a que el precio del producto esté visible
        product_price = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "price-container"))
        )

        # Esperar a que las especificaciones estén visibles
        module_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "additional-attributes-wrapper"))
        )

        # Obtener todas las filas de la tabla con las especificaciones
        table_rows = module_div.find_elements(By.XPATH, ".//table[@id='product-attribute-specs-table']/tbody/tr")

        specs = {}

        if product_name_elements and module_div:
            # Extraemos el nombre del producto
            product_name = product_name_elements[0].text.strip()

            # Extraemos el texto de las especificaciones
            for row in table_rows:
                # Obtener el nombre de la especificación (columna 'th')
                spec_name = row.find_element(By.CLASS_NAME, "label").text.strip()

                # Obtener el valor de la especificación (columna 'td')
                spec_value = row.find_element(By.CLASS_NAME, "data").text.strip()

                # Agregar la especificación al diccionario
                specs[spec_name] = spec_value

            price = product_price[0].text.strip()

            # Retornar el diccionario con 'name', 'price', y 'specs'
            return {'name': product_name, 'price': price, 'specs': specs}

        return None

    except Exception as e:
        print("Error al obtener especificaciones generales:", e)
        return None


# Función principal para realizar el scraping
def scrape_telefonos():
    try:
        # Crear un archivo Excel con múltiples hojas
        with pd.ExcelWriter('Smartphones_DIGICEL_JA-TT.xlsx', engine='xlsxwriter') as writer:

            for country, links in urls.items():
                product_data = []  # Lista para almacenar los datos de todos los productos
                cards_count = 0

                for link in links:
                    driver.get(link)  # Ir a la primera página

                    product_links = get_product_links()

                    if cards_count == 0:
                        # Agregar el "source" en la primera celda de la hoja
                        especificaciones = {'name': link, 'price': '', 'specs': {}}
                        cards_count += 1
                        if especificaciones:
                            product_name = especificaciones['name']
                            specs = especificaciones['specs']
                            price = especificaciones['price']

                            # Crear un diccionario con el nombre del producto y el precio
                            product_entry = {"name": product_name, "price": price}

                            # Agregar cada especificación como una nueva columna
                            for i, (spec_name, spec_value) in enumerate(specs.items()):
                                product_entry[f"spec_{i + 1}_name"] = spec_name
                                product_entry[f"spec_{i + 1}_value"] = spec_value

                            # Agregar la entrada de producto a la lista
                            product_data.append(product_entry)

                    for link in product_links:
                        driver.get(link)

                        # Obtener especificaciones generales

                        especificaciones = get_especificaciones_generales()

                        if especificaciones:
                            product_name = especificaciones['name']
                            specs = especificaciones['specs']
                            price = especificaciones['price']

                            # Crear un diccionario con el nombre del producto y el precio
                            product_entry = {"name": product_name, "price": price}

                            # Agregar cada especificación como una nueva columna
                            for i, (spec_name, spec_value) in enumerate(specs.items()):
                                product_entry[f"spec_{i + 1}_name"] = spec_name
                                product_entry[f"spec_{i + 1}_value"] = spec_value

                            # Agregar la entrada de producto a la lista
                            product_data.append(product_entry)

                # Convertir la lista de diccionarios a un DataFrame de pandas
                df = pd.DataFrame(product_data)

                # Escribir los datos en la hoja correspondiente para cada país
                df.to_excel(writer, sheet_name=country, index=False)

                print("Los datos se han guardado correctamente.")

        driver.quit()

    except Exception as e:
        print(f"Hubo un error: {e}")


scrape_telefonos()
