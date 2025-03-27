import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


# Función para obtener la ruta del chromedriver
def get_chromedriver_path():
    if getattr(sys, 'frozen', False):  # Si el script está empaquetado
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Ruta del chromedriver
    chromedriver_path = os.path.join(base_path, 'chromedriver.exe')
    return chromedriver_path



def scrape_tigo_mbb_data():


    # Configuración del WebDriver
    chromedriver_path = get_chromedriver_path()
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)


    # Lista de URLs por país
    urls = {
        "GT - Prepaid PKG 1": [
            "https://www.tigo.com.gt/prepago/paquetigos#todo-incluido"
        ],
        "GT - Prepaid PKG 2": [
            "https://www.tigo.com.gt/prepago/paquetigos#tigo-flex"
        ],
        "GT - Prepaid PKG 3": [
            "https://www.tigo.com.gt/prepago/paquetigos#datos-o-minutos"
        ],
        "GT - Prepaid PKG 4": [
            "https://www.tigo.com.gt/prepago/paquetigos#contenido"
        ],
        "GT - Postpaid": [
            "https://www.tigo.com.gt/postpago/sin-contrato"
        ],
        "GT - Postpaid Contract": [
            "https://www.tigo.com.gt/postpago/con-contrato"
        ],
        "ESV - PreP internet": [
            "https://www.tigo.com.sv/prepago/recargas-y-paquetes#paquetes-de-internet"
        ],
        "ESV - PreP all included": [
            "https://www.tigo.com.sv/prepago/recargas-y-paquetes#paquetes-todo-incluido"
        ],
        "ESV - Postpaid": [
            "https://www.tigo.com.sv/pospago"
        ],
        "HN - Prepaid pkg": [
            "https://www.tigo.com.hn/prepago/super-recarga-paquetigos#super-recargas"
        ],
        "HN - Paquetigos": [
            "https://www.tigo.com.hn/prepago/super-recarga-paquetigos#paquetigos"
        ],
        "HN - Postpaid": [
            "https://www.tigo.com.hn/postpago"
        ],
        "NI - Prepaid PKG 1": [
            "https://www.tigo.com.ni/superbonos#megapacks"
        ],
        "NI - Prepaid PKG 2": [
            "https://www.tigo.com.ni/superbonos#preplanes"
        ],
        "NI - Prepaid PKG 3": [
            "https://www.tigo.com.ni/superbonos#internet"
        ],
        "NI - Prepaid PKG 4": [
            "https://www.tigo.com.ni/superbonos#minutos-y-sms"
        ],
        "NI - Postpaid": [
            "https://www.tigo.com.ni/pospago"
        ],
        "PA - Prepaid ALL": [
            "https://www.tigo.com.pa/prepago"
        ],
        "PA - Postpaid": [
            "https://www.tigo.com.pa/postpago#linea-nueva"
        ]
    }

    # Usar ExcelWriter para escribir el archivo final
    with pd.ExcelWriter('MBB_tigo_cards_all_countries.xlsx', engine='xlsxwriter') as writer:
        try:
            # Recorrer los URLs de cada país
            for country, links in urls.items():
                for link in links:
                    driver.get(link)

                    # Esperar a que cargue al menos un card dentro de ml-card-product
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.TAG_NAME, "ml-card-product"))
                    )

                    # Lista para almacenar los datos de los cards
                    all_cards = []

                    # Extraer tarjetas visibles en la página actual
                    cards = driver.find_elements(By.TAG_NAME, "ml-card-product")

                    # Se inicia el contador de tarjetas
                    cards_count = 0

                    for card in cards:
                        try:
                            # Verificar si es la primera tarjeta para agregar el "source"
                            if cards_count == 0:
                                # Agregar el "source" en la primera celda de la hoja
                                all_cards.append([link])
                                cards_count += 1

                            # Obtener el texto completo del card
                            card_lines = card.text.split("\n")
                            all_cards.append(card_lines)
                        except Exception as e:
                            print(f"Error extrayendo datos del card: {e}")

                    # Crear un DataFrame con los datos
                    max_columns = max(len(card) for card in all_cards)  # Determinar el número máximo de columnas
                    df = pd.DataFrame(all_cards, columns=[f"Columna {i + 1}" for i in range(max_columns)])

                    # Guardar el DataFrame en una hoja con el nombre del país
                    sheet_name = f"{country}"  # Nombre de la hoja, incluyendo el país

                    # Escribir el DataFrame en la hoja del Excel
                    df.to_excel(writer, index=False, sheet_name=sheet_name)

            print("Datos exportados a 'MBB_tigo_cards_all_countries.xlsx'")

        except Exception as e:
            print(f"Error al procesar los links: {e}")
        finally:
            driver.quit()


scrape_tigo_mbb_data()