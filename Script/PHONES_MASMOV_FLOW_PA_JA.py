from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd
from bs4 import BeautifulSoup
import sys
import os


def get_chromedriver_path():
    if getattr(sys, 'frozen', False):  # Si el script está empaquetado
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Ruta del chromedriver
    chromedriver_path = os.path.join(base_path, 'chromedriver.exe')
    return chromedriver_path



def scrape_digicel_data():
    urls = {
        "JA  - Flow": [
            "https://discoverflow.co/jamaica/deals"
        ],
        "PA - masmovil": [
            "https://www.masmovilpanama.com/promociones/celulares"
        ]
    }


    # Configurar Selenium
    chromedriver_path = get_chromedriver_path()
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)

    # URL de Digicel Jamaica (asegúrate de colocar la correcta)

    with pd.ExcelWriter('Smartphones_FLOW_MASMOV.xlsx', engine='xlsxwriter') as writer:
        for country, links in urls.items():
            for link in links:
                try:
                    driver.get(link)

                    # Esperar a que la página cargue completamente
                    time.sleep(5)

                    # Obtener el HTML de la página
                    soup = BeautifulSoup(driver.page_source, "html.parser")

                    # Encontrar todos los cards de los planes
                    plans = soup.find_all("div", class_="deviceCardContainer")


                    # Lista para almacenar los datos
                    data = []

                    cards_count = 0



                    # Extraer información de cada plan
                    for plan in plans:

                        if cards_count == 0:
                            # Agregar el "source" en la primera celda de la hoja
                            data.append([link])
                            cards_count += 1

                        # Obtener todo el texto dentro del card
                        all_text = [text.strip() for text in plan.stripped_strings]

                        # Agregar los datos a la lista (cada texto en una columna nueva)
                        data.append(all_text)



                    # Determinar el número máximo de columnas (para que todos los cards tengan el mismo formato)
                    max_columns = max(len(row) for row in data)

                    # Rellenar las filas más cortas con None (para que todas tengan el mismo número de columnas)
                    for row in data:
                        row.extend([None] * (max_columns - len(row)))  # Agrega valores vacíos hasta alcanzar max_columns

                    # Generar encabezados genéricos: "Columna 1", "Columna 2", ...
                    column_headers = [f"Columna {i + 1}" for i in range(max_columns)]

                    # Crear un DataFrame de Pandas con los datos
                    df = pd.DataFrame(data, columns=column_headers[:len(data[0])])

                    # Guardar el DataFrame en un archivo Excel
                    sheet_name = f"{country}"
                    df.to_excel(writer, index=False, sheet_name=sheet_name)
                    print(f"Datos guardados para {country} ")
                except Exception as e:
                    print(f"Error al procesar los links: {e}")
        # Cerrar el navegador
        driver.quit()

scrape_digicel_data()