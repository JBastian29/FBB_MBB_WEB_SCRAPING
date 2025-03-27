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



def scrape_tigo_data():


    # Configuración del WebDriver
    # service = Service('C:\\Users\\j84372707\\Desktop\\WEB_SCRAPING_TRIAL\\chromedriver-win64\\chromedriver.exe')  # Cambia esto según la ubicación real del ChromeDriver
    # driver = webdriver.Chrome(service=service)

    # Configuración del WebDriver
    chromedriver_path = get_chromedriver_path()
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)


    # Lista de URLs por país
    urls = {
        "GT - tv+internet ": [
            "https://www.tigo.com.gt/internet/planes#tv-+-internet"
        ],
        "GT - internet ": [
            "https://www.tigo.com.gt/internet/planes#internet"
        ],
        "ESV - internet": [
            "https://www.tigo.com.sv/internet"
        ],
        "ESV - planes": [
            "https://www.tigo.com.sv/planes"
        ],
        "HN - internet": [
            "https://www.tigo.com.hn/internet"
        ],
        "HN - planes": [
            "https://www.tigo.com.hn/planes"
        ],
        "NI - internet": [
            "https://www.tigo.com.ni/internet"
        ],
        "NI - internet tv": [
            "https://www.tigo.com.ni/internet#internet-+-tv"
        ],
        "CR  - internet": [
            "https://www.tigo.cr/internet"
        ],
        "CR - planes": [
            "https://www.tigo.cr/planes"
        ],
        "PA - paquetes": [
            "https://www.tigo.com.pa/internet/paquetes"
        ],
        "PA - paquetes#internet": [
            "https://www.tigo.com.pa/internet/paquetes#internet"
        ]
    }

    # Usar ExcelWriter para escribir el archivo final
    with pd.ExcelWriter('FBB_tigo_cards_all_countries.xlsx', engine='xlsxwriter') as writer:
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

            print("Datos exportados a 'FBB_tigo_cards_all_countries.xlsx'")

        except Exception as e:
            print(f"Error al procesar los links: {e}")
        finally:
            driver.quit()


scrape_tigo_data()