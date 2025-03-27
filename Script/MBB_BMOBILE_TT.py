from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import pandas as pd
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


def scrape_mbb_bmobile_data():
    urls = {
        "Prepaid-day": [
            "https://bmobile.co.tt/mobile/#1701425830707-71723199905242"
        ],
        "Prepaid-month": [
            "https://bmobile.co.tt/mobile/#1701425830810-11723199905242"
        ],
        "Prepaid-plus": [
            "https://bmobile.co.tt/mobile/#1716898857404-5-31723199905242"
        ],
        "Postpaid": [
            "https://bmobile.co.tt/mobile/#1702024199896-2-91723199905242"
        ]
    }

    # Configurar Selenium
    chromedriver_path = get_chromedriver_path()
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)

    with pd.ExcelWriter('MBB_bmobile_plans_full.xlsx', engine='xlsxwriter') as writer:
        for country, links in urls.items():
            for link in links:
                try:
                    driver.get(link)

                    # Esperar a que la página cargue completamente
                    time.sleep(5)


                    if "Prepaid-month" in country:

                        # Buscar el botón con el texto "Líneas nuevas" dentro de este grupo
                        boton = driver.find_element(By.ID,
                                                          "1701425830810-11723199905242")
                        # Hacer clic en el botón
                        boton.click()
                    elif "Prepaid-plus" in country:

                        # Buscar el botón con el texto "Líneas nuevas" dentro de este grupo
                        boton = driver.find_element(By.ID,
                                                          "1716898857404-5-31723199905242")
                        # Hacer clic en el botón
                        boton.click()
                    elif "Postpaid" in country:

                        # Buscar el botón con el texto "Líneas nuevas" dentro de este grupo
                        boton = driver.find_element(By.ID,
                                                          "1702024199896-2-91723199905242")
                        # Hacer clic en el botón
                        boton.click()


                    # Encontrar todos los cards de los planes (divs con la clase 'wpb_column')
                    plans = driver.find_elements(By.CLASS_NAME, "wpb_column")

                    # Lista para almacenar los datos
                    data = []
                    cards_count = 0

                    # Extraer información de cada plan
                    for plan in plans:

                        if cards_count == 0:
                            # Agregar el "source" en la primera celda de la hoja
                            data.append([link])
                            cards_count += 1

                        # Obtener todo el texto dentro del plan
                        all_text = plan.text.strip().split('\n')

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

scrape_mbb_bmobile_data()
