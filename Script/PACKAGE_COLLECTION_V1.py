import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar
from FBB_CLARO_CA5_DR import scrape_claro_data  # Importar la función de Claro
from FBB_TIGO_CA import scrape_tigo_data  # Importar la función de Tigo


class WebScrapingThread(QThread):
    # Definimos señales para actualizar la barra de progreso general y el estado
    progress_general = pyqtSignal(int)  # Para la barra de progreso general
    update_status = pyqtSignal(str)  # Para actualizar el texto de estado

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        try:
            # Scraping Claro
            self.update_status.emit("Claro Scraping is in progess...")
            self.progress_general.emit(0)  # Comienza en 0%
            scrape_claro_data()  # Ejecuta el scraping de Claro
            self.progress_general.emit(50)  # 50% cuando termine Claro
            self.update_status.emit("Claro Scraping is finished!")

            # Scraping Tigo
            self.update_status.emit("Tigo Scraping is in progess...")
            scrape_tigo_data()  # Ejecuta el scraping de Tigo
            self.progress_general.emit(100)  # 100% cuando termine Tigo
            self.update_status.emit("Tigo Scraping is finished!")

        except Exception as e:
            self.update_status.emit(f"Error: {str(e)}")


class WebScrapingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Web Scraping Claro & Tigo')
        layout = QVBoxLayout()

        # Etiqueta de progreso
        self.progress_label = QLabel('Click Start.')
        layout.addWidget(self.progress_label)

        # Botón para iniciar el scraping
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.on_start_button_clicked)
        layout.addWidget(self.start_button)


        # Barra de progreso general
        self.general_progress = QProgressBar(self)
        self.general_progress.setRange(0, 100)
        layout.addWidget(self.general_progress)



        self.setLayout(layout)

    def on_start_button_clicked(self):
        # Desactivar el botón de inicio mientras está en ejecución
        self.start_button.setEnabled(False)
        self.progress_label.setText("Scraping in progress...")

        # Crear y ejecutar el hilo de scraping
        self.scraping_thread = WebScrapingThread()
        self.scraping_thread.progress_general.connect(
            self.general_progress.setValue)  # Conectar la barra de progreso general
        self.scraping_thread.update_status.connect(self.progress_label.setText)  # Actualizar la etiqueta de estado
        self.scraping_thread.finished.connect(self.on_scraping_finished)  # Conectar evento cuando termine

        self.scraping_thread.start()

    def on_scraping_finished(self):
        # Volver a activar el botón cuando termine el proceso
        self.start_button.setEnabled(True)
        self.progress_label.setText("¡Scraping is finished! Files generated")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WebScrapingApp()
    window.show()
    sys.exit(app.exec_())
