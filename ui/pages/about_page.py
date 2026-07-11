from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from utils.constants import VERSION, APP_NAME


class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("About")
        header.setStyleSheet("font-size: 28px; font-weight: 700; color: #e0e0e0;")
        layout.addWidget(header)

        title = QLabel(APP_NAME)
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #533483; margin-top: 12px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        version = QLabel(f"Version {VERSION}")
        version.setStyleSheet("font-size: 14px; color: #888;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 12px;
                padding: 24px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)

        description = QLabel(
            "A modern desktop application for Audio-in-Video Steganography "
            "using Spatial Domain Techniques with automatic algorithm detection."
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 14px; color: #ccc; line-height: 1.6;")
        card_layout.addWidget(description)

        features_title = QLabel("Key Features:")
        features_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #e0e0e0; margin-top: 8px;")
        card_layout.addWidget(features_title)

        features = [
            "10 Spatial Domain Steganography Algorithms",
            "Automatic Algorithm Detection during Extraction",
            "Audio (WAV/MP3) hiding in Video (MP4/MKV/AVI/MOV)",
            "Comprehensive Analysis (PSNR, SSIM, MSE, BER)",
            "Full Algorithm Benchmarking Suite",
            "Modern Dark-Themed Material Design Interface",
        ]
        for feat in features:
            lbl = QLabel(f"  {feat}")
            lbl.setStyleSheet("font-size: 13px; color: #aaa; padding: 2px 0;")
            card_layout.addWidget(lbl)

        tech_title = QLabel("Technology Stack:")
        tech_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #e0e0e0; margin-top: 8px;")
        card_layout.addWidget(tech_title)
        techs = ", ".join([
            "Python 3.12+", "PyQt6", "OpenCV", "NumPy", "Pillow",
            "FFmpeg", "scikit-image", "matplotlib", "PyInstaller"
        ])
        tech_label = QLabel(techs)
        tech_label.setWordWrap(True)
        tech_label.setStyleSheet("font-size: 13px; color: #aaa;")
        card_layout.addWidget(tech_label)

        copyright_label = QLabel("Spatial Domain Steganography Tool")
        copyright_label.setStyleSheet("font-size: 12px; color: #666; margin-top: 16px;")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(copyright_label)

        layout.addWidget(card)
        layout.addStretch()

        scroll.setWidget(container)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)
