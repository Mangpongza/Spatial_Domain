from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame,
    QStatusBar, QSizePolicy,
)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, pyqtSignal
from PyQt6.QtGui import QIcon

from ui.styles.dark_theme import DARK_STYLE, SIDEBAR_STYLE
from ui.pages.dashboard import DashboardPage
from ui.pages.embed_page import EmbedPage
from ui.pages.extract_page import ExtractPage
from ui.pages.analysis_page import AnalysisPage
from ui.pages.benchmark_page import BenchmarkPage
from ui.pages.settings_page import SettingsPage
from ui.pages.about_page import AboutPage


class SideBarButton(QPushButton):
    def __init__(self, text: str, icon_text: str = ""):
        super().__init__(f"  {icon_text}  {text}")
        self.setCheckable(True)
        self.setMinimumHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(SIDEBAR_STYLE)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ซ่อนข้อมูลในวิดีโอ - Spatial Domain Steganography")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        self.setStyleSheet(DARK_STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #0f0f23;
                border-right: 1px solid #0f3460;
            }
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(8, 16, 8, 16)
        sidebar_layout.setSpacing(4)

        logo = QLabel("🎵 StegoPro")
        logo.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: #533483;
            padding: 12px 16px;
            border: none;
            background: transparent;
        """)
        sidebar_layout.addWidget(logo)

        sidebar_layout.addSpacing(16)

        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊", "หน้าแรก"),
            ("embed", "📥", "ฝังเสียง"),
            ("extract", "📤", "ถอนเสียง"),
            ("analysis", "📈", "วิเคราะห์"),
            ("benchmark", "⚡", "ทดสอบ"),
            ("settings", "⚙️", "ตั้งค่า"),
            ("about", "ℹ️", "เกี่ยวกับ"),
        ]

        for key, icon, label in nav_items:
            btn = SideBarButton(label, icon)
            btn.clicked.connect(lambda checked, k=key: self.navigate_to(k))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        sidebar_layout.addStretch()

        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("color: #555; font-size: 11px; padding: 8px; border: none; background: transparent;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version_label)

        main_layout.addWidget(self.sidebar)

        content_area = QVBoxLayout()
        content_area.setContentsMargins(0, 0, 0, 0)
        content_area.setSpacing(0)

        self.stacked_widget = QStackedWidget()
        self.pages = {}
        self.pages["dashboard"] = DashboardPage()
        self.pages["embed"] = EmbedPage()
        self.pages["extract"] = ExtractPage()
        self.pages["analysis"] = AnalysisPage()
        self.pages["benchmark"] = BenchmarkPage()
        self.pages["settings"] = SettingsPage()
        self.pages["about"] = AboutPage()

        for key, page in self.pages.items():
            self.stacked_widget.addWidget(page)
            if hasattr(page, "status_message"):
                page.status_message.connect(self.statusBar().showMessage)

        content_area.addWidget(self.stacked_widget)
        main_layout.addLayout(content_area, 1)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #16213e;
                color: #888;
                border-top: 1px solid #0f3460;
                font-size: 12px;
                padding: 4px 12px;
            }
        """)
        self.status_bar.showMessage("พร้อมทำงาน")

        self.navigate_to("dashboard")

    def navigate_to(self, page_key: str):
        for key, btn in self.nav_buttons.items():
            btn.setChecked(key == page_key)
        if page_key in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[page_key])

    def get_page(self, page_key: str):
        return self.pages.get(page_key)
