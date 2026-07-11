import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow
from controllers.main_controller import MainController


def setup_environment():
    os.makedirs("temp", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)


def main():
    setup_environment()

    app = QApplication(sys.argv)
    app.setApplicationName("Spatial Domain Steganography")
    app.setOrganizationName("SpatialDomain")
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)

    window = MainWindow()
    controller = MainController(window)
    window.controller = controller
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
