from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd
from bs4 import BeautifulSoup
import sys
import os

from selenium.webdriver.common.by import By


def get_chromedriver_path():
    if getattr(sys, 'frozen', False):  # Si el script está empaquetado
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Ruta del chromedriver
    chromedriver_path = os.path.join(base_path, 'chromedriver.exe')
    return chromedriver_path



def scrape_mbb_altice_data():
    urls = {
        "Postpaid": [
            "https://www.altice.com.do/personal/movil/planes/pospago/planes"
        ],
        "Prepaid - alta gama": [
            "https://www.altice.com.do/personal/paqueticos/internet-alta-gama/gigas-alta-gama"
        ],
        "Prepaid - libre": [
            "https://www.altice.com.do/personal/paqueticos/internet-alta-gama/paqueticos-data-libre"
        ]
    }


    # Configurar Selenium
    chromedriver_path = get_chromedriver_path()
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)

    # URL de Digicel Jamaica (asegúrate de colocar la correcta)

    with pd.ExcelWriter('MBB_altice_plans_full.xlsx', engine='xlsxwriter') as writer:
        for country, links in urls.items():
            for link in links:
                try:
                    driver.get(link)

                    # Esperar a que la página cargue completamente
                    time.sleep(5)

                    if "Prepaid - alta gama" in country or "Prepaid - libre" in country:
                        # Buscar todas las tablas en la página
                        if "Prepaid - alta gama" in country:
                            tables = driver.find_elements(By.CLASS_NAME, "table")
                        elif "Prepaid - libre" in country:
                            tables = driver.find_elements(By.CLASS_NAME, "table-responsive")

                        # Iterar sobre cada tabla encontrada
                        for idx, table in enumerate(tables):
                            # Obtener todas las filas de la tabla
                            rows = table.find_elements(By.TAG_NAME, "tr")

                            # Crear una lista para almacenar los datos
                            data = []
                            cards_count = 0

                            # Iterar sobre las filas de la tabla
                            for row in rows:
                                if cards_count == 0:
                                    # Agregar el "source" en la primera celda de la hoja
                                    data.append([link])
                                    cards_count += 1
                                cells = row.find_elements(By.TAG_NAME, "td")
                                cell_data = [cell.text.strip() for cell in cells]  # Extraer el texto de cada celda
                                if cell_data:  # Solo agregar filas que tengan datos
                                    data.append(cell_data)

                            # Determinar el número máximo de columnas
                            max_columns = max(len(row) for row in data)

                            # Rellenar las filas más cortas con None
                            for row in data:
                                row.extend([None] * (max_columns - len(row)))

                            # Generar encabezados genéricos: "Columna 1", "Columna 2", ...
                            column_headers = [f"Columna {i + 1}" for i in range(max_columns)]

                            # Crear un DataFrame de Pandas con los datos
                            df = pd.DataFrame(data, columns=column_headers[:len(data[0])])

                            # Guardar cada tabla con un nombre distinto
                            sheet_name = f"{country}_tabla_{idx + 1}"
                            df.to_excel(writer, index=False, sheet_name=sheet_name)
                            print(f"Datos guardados para {country} - tabla {idx + 1}")

                    else:
                        # Continuar con la lógica existente para otros planes
                        soup = BeautifulSoup(driver.page_source, "html.parser")

                        # Encontrar todos los cards de los planes
                        plans = soup.find_all("div", class_="plan-item")

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

                        # Determinar el número máximo de columnas
                        max_columns = max(len(row) for row in data)

                        # Rellenar las filas más cortas con None
                        for row in data:
                            row.extend([None] * (max_columns - len(row)))

                        # Generar encabezados genéricos
                        column_headers = [f"Columna {i + 1}" for i in range(max_columns)]

                        # Crear un DataFrame de Pandas con los datos
                        df = pd.DataFrame(data, columns=column_headers[:len(data[0])])

                        # Guardar el DataFrame
                        sheet_name = f"{country}"
                        df.to_excel(writer, index=False, sheet_name=sheet_name)
                        print(f"Datos guardados para {country}")

                except Exception as e:
                    print(f"Error al procesar los links: {e}")

        # Cerrar el navegador
        driver.quit()

scrape_mbb_altice_data()