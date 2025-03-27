from selenium import webdriver
from selenium.webdriver import ActionChains
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



def scrape_mbb_kolbi_data():
    urls = {

        "Prepaid - unlimited int": [
            "https://www.kolbi.cr/wps/portal/kolbi_dev/personas/prepago/opciones-prepago/paquetes-internet-prepago/Paquetes+Internet+ilimitado"
        ],
        "Prepaid - entertainment": [
            "https://www.kolbi.cr/wps/portal/kolbi_dev/personas/prepago/opciones-prepago/paquetes-internet-prepago/entretenimiento"
        ],
        "Prepaid - internet": [
            "https://www.kolbi.cr/wps/portal/kolbi_dev/personas/prepago/opciones-prepago/paquetes-internet-prepago/prepago-paquetesinternet"
        ],
        "Postpaid - PKG1": [
            "https://www.kolbi.cr/wps/portal/kolbi_dev/personas/postpago/planes-postpago/internet-postpago"
        ],
        "Postpaid - PKG2": [
            "https://www.kolbi.cr/wps/portal/kolbi_dev/personas/postpago/planes-postpago/planes-ultrak"
        ],
        "Postpaid - internet": [
            "https://www.kolbi.cr/wps/portal/kolbi_dev/personas/postpago/planes-postpago/planes-ultrak/planes-kolbi-datos"
        ]
    }


    # Configurar Selenium
    chromedriver_path = get_chromedriver_path()
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)

    # URL de Digicel Jamaica (asegúrate de colocar la correcta)

    with pd.ExcelWriter('MBB_kolbi_plans_full.xlsx', engine='xlsxwriter') as writer:
        for country, links in urls.items():
            for link in links:
                try:
                    driver.get(link)

                    # Esperar a que la página cargue completamente
                    time.sleep(5)

                    # Obtener el HTML de la página
                    soup = BeautifulSoup(driver.page_source, "html.parser")


                    if country == "Postpaid - PKG2":

                        # Lista para almacenar los datos
                        data = []
                        cards_count = 0

                        # Encuentra todos los botones "Ver Detalle"
                        buttons = driver.find_elements(By.CLASS_NAME, "btnDetallePlan")
                        table = driver.find_element(By.CLASS_NAME, "table")

                        # Guardar las filas que ya fueron procesadas para evitar duplicados
                        processed_rows = set()

                        # Itera sobre cada botón
                        for button in buttons:
                            try:
                                # Mueve el mouse al botón y haz clic
                                ActionChains(driver).move_to_element(button).click().perform()

                                # Espera un poco para asegurarte de que la tabla se haya expandido
                                time.sleep(2)  # Ajusta el tiempo según el rendimiento de la página

                                # Recupera las filas de la tabla
                                rows = table.find_elements(By.TAG_NAME, "tr")

                                # Procesar las filas de la tabla
                                for row in rows:
                                    cells = row.find_elements(By.TAG_NAME, "td")
                                    if cells:  # Solo procesar filas que tengan celdas (y no encabezados vacíos)
                                        # Extraer el texto de cada celda
                                        cell_data = [cell.text.strip() for cell in cells]

                                        # Convertir la fila en una tupla (para usarla como un identificador único)
                                        row_identifier = tuple(cell_data)

                                        # Si la fila no ha sido procesada, agregarla
                                        if row_identifier not in processed_rows:
                                            processed_rows.add(row_identifier)  # Marcar esta fila como procesada
                                            if cards_count == 0:
                                                # Agregar el "source" en la primera celda de la hoja (si es necesario)
                                                data.append([link])  # Asegúrate de tener definida la variable `link`
                                                cards_count += 1
                                            data.append(cell_data)  # Agregar la fila a los datos

                                # Opcional: Espera para no sobrecargar la página, si es necesario
                                # time.sleep(1)

                            except Exception as e:
                                print(f"Error al hacer clic en el botón: {e}")
                                continue  # Continuar con el siguiente botón si ocurre un error

                    elif country == "Postpaid - internet":
                        data = []
                        cards_count = 0
                        table = driver.find_element(By.CLASS_NAME, "table")
                        rows = table.find_elements(By.TAG_NAME, "tr")

                        for row in rows:
                            if cards_count == 0:
                                # Agregar el "source" en la primera celda de la hoja
                                data.append([link])
                                cards_count += 1
                            cells = row.find_elements(By.TAG_NAME, "td")
                            cell_data = [cell.text.strip() for cell in cells]  # Extraer el texto de cada celda
                            if cell_data:  # Solo agregar filas que tengan datos
                                data.append(cell_data)

                    else:

                        # Encontrar todos los cards de los planes
                        plans = soup.find_all("div", class_="paquetes-kolbi")

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

scrape_mbb_kolbi_data()