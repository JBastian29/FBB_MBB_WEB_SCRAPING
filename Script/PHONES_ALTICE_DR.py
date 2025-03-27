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
            "https://www.altice.com.do/tienda?search_api_fulltext=&sort_bef_combine=title_ASC&sort_by=title&sort_order=ASC&page=0"
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

    time.sleep(3)

    product_links = []

    # Encontrar todos los artículos de productos
    product_elements = driver.find_elements(By.CLASS_NAME, "p-a")

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
                                            "commerce-product-title.brand-type"))
        )

        # Esperar a que el botón "Prepago" sea clickeable y hacer clic en él
        prepago_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@role='tablist']//a[contains(text(), 'Prepago')]"))
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
                                            "commerce-product-title.brand-type"))
        )

        # Esperar a que el precio del producto esté visible
        product_price = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "fpv-price"))
        )

        # Esperar a que las especificaciones estén visibles
        module_divs = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "caracteristicas.m-b"))
        )

        if product_name_elements and module_divs:
            # Extraemos el nombre del producto
            product_name = product_name_elements.text.strip()

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
        page = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.pager__item.is-active.active a"))
        )

        actual_page = int(page.text.strip().replace("Página actual", "").strip())


        if actual_page < page_number:
            break


        print(f"Obteniendo enlaces de la página {page_number}")
        product_links = get_product_links(page_number)

        if not product_links:
            break

        all_product_links.extend(product_links)

        # Comprobar si hay más páginas
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "li.pager__item.pager__item--next a")
        except Exception as e:
            break
        if "disabled" in next_button.get_attribute("class"):
            break


        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(3)
        page_number += 1

    return all_product_links


# Función principal para realizar el scraping
def scrape_telefonos():
    try:
        # Crear un archivo Excel con múltiples hojas
        with pd.ExcelWriter('Smartphones_DR_ALTICE.xlsx', engine='xlsxwriter') as writer:
            for country, links in urls.items():
                product_data = []

                for link in links:
                    driver.get(link)  # Ir a la primera página

                    product_links = navigate_pages()
                    #product_links = ['https://www.altice.com.do/tienda/productos/moviles/mobiwire/altice-s14?v=421481']

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

                # Convertir la lista de diccionarios a un DataFrame de pandas
                df = pd.DataFrame(product_data)

                # Escribir los datos en la hoja correspondiente para cada país
                df.to_excel(writer, sheet_name=country, index=False)

            print("Los datos se han guardado correctamente.")

        driver.quit()

    except Exception as e:
        print(f"Hubo un error: {e}")


scrape_telefonos()
