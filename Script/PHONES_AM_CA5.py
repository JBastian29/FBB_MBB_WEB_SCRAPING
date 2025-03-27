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
        "GT": [
            "https://tiendaenlinea.claro.com.gt/categories/prepago/celulares?utm_source=menuheader&utm_medium=celulares&utm_campaign=portal%2F&page=1&pagesize=20"
        ],
        "ESV": [
            "https://tiendaenlinea.claro.com.sv/categories/prepago/celulares?utm_source=menuheader&utm_medium=celulares&utm_campaign=portal%2F&pagesize=20&page=1"
        ],
        "HN": [
            "https://tiendaenlinea.claro.com.hn/categories/prepago/celulares?automatic=&utm_source=menuheader&utm_medium=celulares&utm_campaign=portal%2F&pagesize=20&page=1"
        ],
        "NI": [
            "https://tiendaenlinea.claro.com.ni/categories/prepago/celulares?utm_source=menuheader&utm_medium=celulares&utm_campaign=portal/"
        ],
        "CR": [
            "https://tiendaenlinea.claro.cr/categories/prepago/celularesprepago?automatic&utm_source=menuheader&utm_medium=tiendaenlineacelulares&utm_campaign=portal"
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
        product_elements = driver.find_elements(By.CSS_SELECTOR, "article.product--box a.max95")
        for product in product_elements:
            link = product.get_attribute("href")
            product_links.append(link)
        return product_links
    except Exception as e:
        print(f"Error al obtener enlaces de productos en la página {page_number}: {e}")
        return []

# Función para hacer clic en "Ficha Técnica"
def click_ficha_tecnica():
    try:
        product_name_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "product--header"))
        )
        ficha_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ficha"))
        )
        ficha_button.click()
        time.sleep(2)
    except Exception as e:
        print("Error al hacer clic en 'Ficha Técnica':", e)

# Función para obtener las especificaciones generales
def get_especificaciones_generales():
    try:
        product_name_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "product--header"))
        )
        product_price = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "price.is-promo"))
        )
        module_divs = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "product--datasheet"))
        )

        if product_name_elements and module_divs:
            product_name = product_name_elements[0].text.strip()
            specs = module_divs[0].text.strip()
            price = product_price[0].text.strip()
            return {'name': product_name, 'price': price, 'specs': specs}
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
                EC.presence_of_all_elements_located((By.CLASS_NAME, "pagination--page.active"))
            )
            actual_page = page[0].text.strip()

            if int(actual_page) < page_number:
                break

            print(f"Obteniendo enlaces de la página {page_number}")
            product_links = get_product_links(page_number)

            if not product_links:
                break

            all_product_links.extend(product_links)

            next_button = driver.find_element(By.ID, "pagination-next")
            if "disabled" in next_button.get_attribute("class"):
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
        with pd.ExcelWriter('Smartphones_AM_CA5.xlsx', engine='xlsxwriter') as writer:
            for country, links in urls.items():
                product_data = []

                for link in links:
                    try:
                        driver.get(link)
                        product_links = navigate_pages()

                        for link in product_links:
                            try:
                                driver.get(link)
                                time.sleep(5 if country != "GT" else 6)

                                click_ficha_tecnica()
                                especificaciones = get_especificaciones_generales()

                                if especificaciones:
                                    product_name = especificaciones['name']
                                    specs = especificaciones['specs']
                                    price = especificaciones['price']
                                    specs_list = specs.split('\n')

                                    product_entry = {"name": product_name, "price": price}
                                    for i, spec in enumerate(specs_list):
                                        product_entry[f"spec_{i + 1}"] = spec.strip()

                                    product_data.append(product_entry)
                            except Exception as e:
                                print(f"Error al procesar el producto {link}: {e}")
                                continue

                    except Exception as e:
                        print(f"Error al procesar la URL {link}: {e}")
                        continue

                df = pd.DataFrame(product_data)
                df.to_excel(writer, sheet_name=country, index=False)

            print("Los datos se han guardado correctamente en 'AM_CA5_Smartphones.xlsx'.")

        driver.quit()

    except Exception as e:
        print(f"Hubo un error: {e}")

scrape_telefonos()
