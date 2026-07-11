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
    app.setApplicationName("ซ่อนข้อมูลในวิดีโอ (Spatial Domain Steganography)")
    app.setOrganizationName("SpatialDomain")
    # PyQt6 handles HighDPI scaling automatically (AA_UseHighDpiPixmaps
    # and AA_EnableHighDpiScaling were removed -- they only exist in PyQt5)

    window = MainWindow()
    controller = MainController(window)
    window.controller = controller
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
