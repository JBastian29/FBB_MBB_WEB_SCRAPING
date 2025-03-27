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
        "ALL": [
            "https://www.kolbi.cr/wps/portal/kolbi_dev/personas/telefonos/telefonos#/"
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

    time.sleep(3)

    product_links = []

    # Encontrar todos los artículos de productos
    product_elements = driver.find_elements(By.CLASS_NAME, "cellphone-thumbnail")

    # Obtener los links de los productos
    for product in product_elements:
        try:
            # Localizar el elemento <a> dentro del producto
            link_element = product.find_element(By.TAG_NAME, "a")

            # Obtener el atributo href del enlace
            link = link_element.get_attribute("href")

            # Agregar el enlace a la lista
            if link:  # Solo agregar si el enlace no está vacío
                product_links.append(link)
        except Exception as e:
            print("Error al obtener el enlace de un producto:", e)

    return product_links


# Función para hacer clic en "Ficha Técnica"
def click_en_prepago():
    try:
        # Esperar a que los elementos del nombre del producto estén presentes
        product_name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME,
                                            "title-black"))
        )

        # Esperar a que el botón "Prepago" sea clickeable y hacer clic en él
        prepago_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "label.label-radio-coralcr[for='rbtKitPrepago']"))
        )
        prepago_button.click()
        time.sleep(2)


    except Exception as e:
        print("Error al hacer clic en 'Prepago':", product_name_element[0].text.strip(), "\n ", e)


# Función para obtener las especificaciones generales
def get_especificaciones_generales():
    try:
        # Esperar a que el nombre del producto esté visible
        product_name_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME,
                                            "title-black"))
        )

        # Esperar a que el botón esté presente en el DOM
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "btnCapacidades"))
        )

        # Localizar el <span> dentro del botón
        span_element = button.find_element(By.CLASS_NAME, "selection")



        # Esperar a que la tabla esté presente en el DOM
        table_body = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "prePagoTblBody"))
        )

        # Localizar la primera fila de la tabla
        first_row = table_body.find_element(By.TAG_NAME, "tr")

        # Localizar el segundo <td> dentro de la fila
        product_price = first_row.find_elements(By.TAG_NAME, "td")[1]  # El índice 1 representa el segundo <td>


        if product_name_elements:
            # Extraemos el nombre del producto
            product_name = product_name_elements.text.strip()

            price = product_price.text.strip()

            specs = span_element.text.strip()


            # Retornar el diccionario con 'name' y 'specs'
            return {'name': product_name, 'price': price, 'specs':specs}

        # Si no se encuentra el producto o las especificaciones, retornar None
        return None

    except Exception as e:
        print("Error al obtener especificaciones generales:", e)
        return None



# Función principal para realizar el scraping
def scrape_telefonos():
    try:
        # Crear un archivo Excel con múltiples hojas
        with pd.ExcelWriter('Smartphones_CR_KOLBI.xlsx', engine='xlsxwriter') as writer:
            for country, links in urls.items():
                product_data = []

                for link in links:
                    driver.get(link)  # Ir a la primera página

                    product_links = get_product_links()

                    for link in product_links:
                        driver.get(link)


                        # Hacer clic en "Ficha Técnica"
                        try:
                            click_en_prepago()
                        except Exception as e:
                            continue

                        # Obtener especificaciones generales
                        especificaciones = get_especificaciones_generales()

                        if especificaciones:
                            product_name = especificaciones['name']
                            price = especificaciones['price']
                            specs = especificaciones['specs']


                            # Crear un diccionario con el nombre y las especificaciones
                            product_entry = {"name": product_name, "price": price, "specs": specs}

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
