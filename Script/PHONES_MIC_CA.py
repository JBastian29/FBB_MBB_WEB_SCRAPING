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
        "ESV": [
            "https://www.tigo.com.sv/catalogo-prepago"
        ],
        "HN": [
            "https://www.tigo.com.hn/smartphones-prepago"
        ],
        "NI": [
            "https://www.tigo.com.ni/catalogo-prepago"
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
def get_product_links(page_number):
    try:
        time.sleep(3)
        product_links = []

        # Encontrar todos los artículos de productos
        product_elements = driver.find_elements(By.CLASS_NAME, "button.is-primary")

        # Obtener los links de los productos
        for product in product_elements:
            if product.get_attribute("href") is not None:
                link = product.get_attribute("href")
                product_links.append(link)

        return product_links
    except Exception as e:
        print(f"Error al obtener enlaces de productos en la página {page_number}: {e}")
        return []


# Función para obtener las especificaciones generales
def get_especificaciones_generales():
    try:
        # Esperar a que el nombre del producto esté visible
        product_name_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "mb-4"))
        )

        # Esperar a que el precio del producto esté visible
        product_price = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "is-size-4.text-secondary"))
        )

        # Esperar a que las especificaciones estén visibles
        module_divs = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "table.is-striped.is-size-9"))
        )

        if product_name_elements and module_divs:
            # Extraemos el nombre del producto
            product_name = product_name_elements[1].text.strip()

            # Extraemos el texto de las especificaciones (puedes elegir otro índice si es necesario)
            specs = module_divs[0].text.strip()

            price = product_price[0].text.strip()

            # Retornar el diccionario con 'name' y 'specs'
            return {'name': product_name, 'price': price, 'specs': specs}

        # Si no se encuentra el producto o las especificaciones, retornar None
        return None
    except Exception as e:
        print("Error al obtener especificaciones generales:", e)
        return None


# Función para navegar a través de las páginas
def navigate_pages():
    page_number = 1
    all_product_links = []

    while True:
        try:
            page = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "page-item.is-active"))
            )


            actual_page = page[0].text.strip()

            if int(actual_page) < page_number:
                break

            print(f"Obteniendo enlaces de la página {page_number}")
            product_links = get_product_links(page_number)

            if not product_links:
                break

            all_product_links.extend(product_links)

            # Comprobar si hay más páginas
            next_button = driver.find_element(By.CLASS_NAME, "page-button-next")
            if "disabled" in next_button.get_attribute("class") or next_button.get_attribute("disabled") == "true":
                break

            next_button.click()
            time.sleep(3)
            page_number += 1
        except Exception as e:
            print(f"Error al navegar por las páginas: {e}")
            break

    return all_product_links


# Función principal para realizar el scraping
def scrape_telefonos():
    try:
        # Crear un archivo Excel con múltiples hojas
        with pd.ExcelWriter('Smartphones_MIC_CA.xlsx', engine='xlsxwriter') as writer:
            for country, links in urls.items():
                product_data = []

                for link in links:
                    try:
                        driver.get(link)  # Ir a la primera página


                        product_links = navigate_pages()

                        if product_links == []:
                            product_links = get_product_links(link)


                        for link in product_links:
                            try:
                                driver.get(link)

                                if country != "GT":
                                    time.sleep(8)
                                else:
                                    time.sleep(6)

                                # Obtener especificaciones generales
                                especificaciones = get_especificaciones_generales()

                                if especificaciones:
                                    product_name = especificaciones['name']
                                    specs = especificaciones['specs']
                                    price = especificaciones['price']

                                    # Dividir las especificaciones por líneas o algún delimitador (si es necesario)
                                    specs_list = specs.split('\n')  # Cambia el delimitador según el formato real

                                    # Crear un diccionario con el nombre y las especificaciones
                                    product_entry = {"name": product_name, "price": price}
                                    for i, spec in enumerate(specs_list):
                                        product_entry[
                                            f"spec_{i + 1}"] = spec.strip()  # Asigna cada especificación a una columna nueva

                                    product_data.append(product_entry)
                            except Exception as e:
                                print(f"Error al procesar el enlace {link}: {e}")
                                continue
                    except Exception as e:
                        print(f"Error al procesar el país {country}: {e}")
                        continue

                # Convertir la lista de diccionarios a un DataFrame de pandas
                df = pd.DataFrame(product_data)

                # Escribir los datos en la hoja correspondiente para cada país
                df.to_excel(writer, sheet_name=country, index=False)

        print("Los datos se han guardado correctamente en 'MIC_CA_Smartphones.xlsx'.")
    except Exception as e:
        print(f"Hubo un error: {e}")
    finally:
        driver.quit()


# Ejecutar la función pr
scrape_telefonos()
