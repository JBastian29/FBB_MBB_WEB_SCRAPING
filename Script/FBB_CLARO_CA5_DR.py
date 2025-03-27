import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

def scrape_claro_data():


    # Configuración del WebDriver
    # service = Service('C:\\Users\\j84372707\\Desktop\\WEB_SCRAPING_TRIAL\\chromedriver-win64\\chromedriver.exe')
    # driver = webdriver.Chrome(service=service)

    # Configuración del WebDriver
    chromedriver_path = get_chromedriver_path()
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)

    # Lista de URLs por país
    urls = {
        "CR  - 2play Fiber": [
            "https://www.claro.cr/personas/servicios/servicios-hogar/doble-play/planes-y-precios/"
        ],
        "CR  - 3play Fiber": [
            "https://www.claro.cr/personas/servicios/servicios-hogar/triple-play/planes-y-precios/"
        ],
        "CR  - 2play": [
            "https://www.claro.cr/personas/servicios/servicios-hogar/2-play/planes-y-precios/"
        ],
        "CR  - 3play": [
            "https://www.claro.cr/personas/servicios/servicios-hogar/3-play/planes-y-precios/"
        ],
        "CR  - internet Fiber": [
            "https://www.claro.cr/personas/servicios/servicios-hogar/internet-fibra-optica/"
        ],
        "DR  - ALL internet": [
            "https://www.claro.com.do/personas/servicios/servicios-hogar/planes-y-precios/"
        ],
        "SV  - ALL internet": [
            "https://www.claro.com.sv/personas/servicios/claro-hogar/internet/planes-y-precios/"
        ],
        "SV  - tv+internet": [
            "https://www.claro.com.sv/personas/servicios/servicios-hogar/claro-tv-plus/"
        ],
        "GT  - ALL internet": [
            "https://www.claro.com.gt/personas/servicios/servicios-hogar/planes-y-precios/"
        ],
        "HN  - ALL internet": [
            "https://www.claro.com.hn/personas/servicios/servicios-hogar/planes-y-precios/"
        ],
        "NI  - ALL internet": [
            "https://www.claro.com.ni/personas/servicios/servicios-hogar/planes-y-precios/"
        ]
    }
    with pd.ExcelWriter('FBB_claro_cards_all_countries.xlsx', engine='xlsxwriter') as writer:
        try:
            for country, links in urls.items():
                for link in links:
                    try:
                        # URL de la página
                        driver.get(link)

                        # Esperar a que el contenido inicial cargue
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "cPlanV2"))
                        )

                        # Lista para almacenar los datos
                        all_cards = []
                        seen_indexes = set()
                        last_page_number = "1"  # Página inicial
                        cards_count = 0

                        while True:
                            # Primer caso: Si encuentra sliderTabsViewplanesDestacados y slick-track
                            try:
                                # Buscar el contenedor específico de tarjetas
                                slider_container = driver.find_element(By.CLASS_NAME, "sliderTabsViewplanesDestacados")
                                slick_track = slider_container.find_element(By.CLASS_NAME, "slick-track")
                                print("Encontrado componente slick-track. Extrayendo planes desde slick-track...")

                                # Encontrar los botones de paginación en el componente slick-dots dentro del contenedor
                                pages_slick_track = slider_container.find_elements(By.CSS_SELECTOR, "ul.slick-dots li button")

                                for page_button in pages_slick_track:
                                    page_number = page_button.text
                                    if page_number not in seen_indexes:  # Validar que el índice de la página no se repita
                                        # Hacer clic en el botón de página
                                        page_button.click()
                                        time.sleep(3)  # Esperar a que la página se cargue

                                        # Extraer las tarjetas (slick-slide) visibles dentro de 'slick-track' en el contenedor
                                        cards = slider_container.find_elements(By.CLASS_NAME, "slick-slide")

                                        for card in cards:
                                            # Verificar si la tarjeta está activa y visible
                                            if "slick-active" in card.get_attribute("class"):
                                                # Obtener el atributo data-index de la tarjeta
                                                data_index = card.get_attribute("data-index")


                                                if cards_count == 0:
                                                    # Agregar el "source" en la primera celda de la hoja
                                                    all_cards.append([link])
                                                    cards_count += 1


                                                # Verificar si el data-index ya ha sido procesado
                                                if data_index not in seen_indexes:
                                                    # Obtener el texto del card y dividirlo
                                                    card_lines = card.text.split("\n")
                                                    all_cards.append(card_lines)  # Guardar cada línea como una columna

                                                    # Marcar el data-index como procesado
                                                    seen_indexes.add(data_index)

                                        # Marcar la página como procesada
                                        seen_indexes.add(page_number)

                                # Verificar si ya hemos recorrido todas las páginas
                                if len(seen_indexes)-1 == len(pages_slick_track):
                                    print("Ya no hay más páginas para recorrer.")
                                    break

                            except Exception as e:
                                print(f"No se encontró el componente slick-track. Extrayendo desde cPlanV2...")

                            try:

                                # Segundo caso: Si no se encuentra el componente slick-track, extraer desde 'cPlanV2'
                                cards = driver.find_elements(By.CLASS_NAME, "cPlanV2")
                                if cards_count == 0:
                                    # Agregar el "source" en la primera celda de la hoja
                                    all_cards.append([link])
                                    cards_count += 1
                                for card in cards:
                                    # Dividir el contenido de la tarjeta en líneas
                                    card_lines = card.text.split("\n")
                                    all_cards.append(card_lines)  # Guardar cada línea como una columna

                                # Verificar el número de la página actual antes de hacer clic en "Siguiente"

                                current_page = driver.find_element(
                                    By.CSS_SELECTOR, "li.paginationMolPage.paginationMolActive a"
                                ).text  # Extraer el número de la página actual

                                # Intentar hacer clic en el botón "Siguiente"
                                try:
                                    next_button = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, "li.paginationMolNext a"))
                                    )
                                    next_button.click()
                                    time.sleep(3)  # Esperar a que cargue la nueva página
                                except Exception as e:
                                    print(f"No hay más páginas disponibles.")
                                    break

                                # Verificar si el número de la página actual ha cambiado
                                new_page_number = driver.find_element(
                                    By.CSS_SELECTOR, "li.paginationMolPage.paginationMolActive a"
                                ).text
                                if new_page_number == last_page_number:
                                    print("El número de página no cambió. Fin de la paginación.")
                                    break
                                else:
                                    last_page_number = new_page_number

                            except Exception as e:
                                print(f"No se pudo encontrar el indicador de página actual.")
                                break

                        # Crear un DataFrame con los datos
                        max_columns = max(len(card) for card in all_cards)  # Determinar el número máximo de columnas
                        df = pd.DataFrame(all_cards, columns=[f"Columna {i+1}" for i in range(max_columns)])

                        # Guardar el DataFrame en un archivo Excel
                        sheet_name = f"{country}"
                        df.to_excel(writer, index=False, sheet_name=sheet_name)

                        print("Se han guardado los datos de todas las tarjetas.")
                    except Exception as e:
                        print(f"Error al procesar los links: {e}")

        except Exception as e:
            print(f"Error en la escritura final del archivo de Excel: {e}")
        finally:
            driver.quit()

scrape_claro_data()