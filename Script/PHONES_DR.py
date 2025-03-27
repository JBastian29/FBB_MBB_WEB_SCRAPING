import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd



def get_chromedriver_path():
    if getattr(sys, 'frozen', False):  # Si el script está empaquetado
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Ruta del chromedriver
    chromedriver_path = os.path.join(base_path, 'chromedriver.exe')
    return chromedriver_path


chromedriver_path = get_chromedriver_path()
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)

# URL principal
base_url = "https://tienda.claro.com.do/movil"


# Función para obtener los enlaces de los productos
def get_product_links():
    product_links = []
    driver.get(base_url)

    # Extraer enlaces de cada producto de las páginas
    while True:
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            product_cards = soup.find_all('div', class_='product-card')

            # Obtener el enlace de cada producto
            for card in product_cards:
                link = card.find('a', {'class': 'btn btn-primary'})['href']
                full_link = f"https://tienda.claro.com.do{link}"
                product_links.append(full_link)

            # Verificar si hay una siguiente página
            try:
                next_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "li.c-pagination__item.c-pagination__item--next a")))
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)  # Esperar a que cargue la nueva página
            except Exception as e:
                print(f"No hay más páginas disponibles.")
                break
        except Exception as e:
            print(f"Error al obtener enlaces de productos: {e}")
            continue

    return product_links


# Función para extraer información del detalle de cada producto
def extract_product_info(product_url):
    try:
        driver.get(product_url)

        # Esperar a que el contenido cargue y el botón 'Prepago' esté disponible
        prepago_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'Prepago')))

        # Hacer clic en el botón 'Prepago'
        driver.execute_script("arguments[0].click();", prepago_button)
        time.sleep(6)  # Esperar que la información cargue

        # Extraer datos con BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Obtener título del producto
        title = soup.find('h2', class_='--emr-title').text.strip()

        # Obtener precio utilizando el nuevo selector para "Pago Total"
        price_label = soup.find('label', {'for': 'payment-method-0'})  # Buscar el label con el for='payment-method-0'
        if price_label:
            price = price_label.find('span', class_='--emr-data').text.strip()  # Obtener el precio
        else:
            price = "Precio no encontrado"

        # Extraer todas las características del producto
        features = soup.find_all('div', class_='--emr-item')
        feature_data = []

        for feature in features:
            label = feature.find('p', class_='--emr-label')  # Etiqueta de la característica
            data = feature.find('p', class_='--emr-data')   # Valor de la característica
            if label and data:
                feature_data.append(f"{label.text.strip()}: {data.text.strip()}")  # Formato: "Etiqueta: Valor"

        # Asegurarse de que las características sean del mismo tamaño que las columnas
        # Rellenar las celdas vacías si el número de características es menor que las columnas
        feature_data += [''] * (20 - len(feature_data))  # Ajusta el número20 según el número máximo de características que esperas

        # Almacenar los datos extraídos
        product_info = {
            'Title': title,
            'Price': price,
        }

        # Crear claves para cada característica y agregarlas al diccionario
        for i, feature in enumerate(feature_data, start=1):
            product_info[f'Feature {i}'] = feature

        return product_info
    except Exception as e:
        print(f"Error al extraer información del producto {product_url}: {e}")
        return None


# Función principal de scraping
def main():
    product_links = get_product_links()
    all_product_data = []

    # Extraer los datos de cada producto
    for link in product_links:
        product_data = extract_product_info(link)
        if product_data:  # Solo agregar si se extrajeron datos correctamente
            all_product_data.append(product_data)

    driver.quit()  # Cerrar el driver una vez que se hayan extraído todos los datos

    # Guardar los datos en un DataFrame
    df = pd.DataFrame(all_product_data)

    # Escribir los datos en un archivo CSV
    df.to_csv('Smartphones_AM_DR.csv', index=False,  encoding='utf-8-sig')
    print("Datos extraídos y guardados en AM_DR_Smartphones.csv")


if __name__ == "__main__":
    main()
