DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}

QPushButton {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #0f3460;
    border-color: #533483;
}
QPushButton:pressed {
    background-color: #533483;
}
QPushButton:disabled {
    background-color: #2a2a3e;
    color: #666;
}

QLabel {
    color: #e0e0e0;
    font-size: 13px;
}

QComboBox {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    min-height: 20px;
}
QComboBox:hover {
    border-color: #533483;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #e0e0e0;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    selection-background-color: #533483;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #533483;
}

QGroupBox {
    border: 1px solid #0f3460;
    border-radius: 8px;
    margin-top: 16px;
    padding: 16px 12px 12px 12px;
    font-size: 14px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    padding: 0 8px;
    color: #533483;
}

QScrollBar:vertical {
    background: #1a1a2e;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #0f3460;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #533483;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #1a1a2e;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background: #0f3460;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background: #533483;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QTabWidget::pane {
    border: 1px solid #0f3460;
    border-radius: 8px;
    background-color: #1a1a2e;
}
QTabBar::tab {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QTabBar::tab:selected {
    background-color: #533483;
    border-color: #533483;
}
QTabBar::tab:hover {
    background-color: #0f3460;
}

QTableWidget, QTableView {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 6px;
    gridline-color: #0f3460;
}
QTableWidget::item, QTableView::item {
    padding: 6px;
}
QTableWidget::item:selected, QTableView::item:selected {
    background-color: #533483;
}
QHeaderView::section {
    background-color: #0f3460;
    color: #e0e0e0;
    padding: 8px;
    border: none;
    font-weight: 600;
}

QProgressBar {
    border: 1px solid #0f3460;
    border-radius: 6px;
    text-align: center;
    color: #e0e0e0;
    font-size: 12px;
    background-color: #16213e;
    height: 20px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #533483, stop:0.5 #0f3460, stop:1 #533483);
    border-radius: 5px;
}

QSlider::groove:horizontal {
    background: #16213e;
    border: 1px solid #0f3460;
    height: 6px;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #533483;
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background: #7b5ea7;
}

QCheckBox {
    spacing: 8px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #0f3460;
    border-radius: 4px;
    background-color: #16213e;
}
QCheckBox::indicator:checked {
    background-color: #533483;
    border-color: #533483;
}

QRadioButton {
    spacing: 8px;
    font-size: 13px;
}
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #0f3460;
    border-radius: 10px;
    background-color: #16213e;
}
QRadioButton::indicator:checked {
    background-color: #533483;
    border-color: #533483;
}

QMenuBar {
    background-color: #16213e;
    color: #e0e0e0;
    border-bottom: 1px solid #0f3460;
}
QMenuBar::item:selected {
    background-color: #533483;
}
QMenu {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
}
QMenu::item:selected {
    background-color: #533483;
}

QStatusBar {
    background-color: #16213e;
    color: #888;
    border-top: 1px solid #0f3460;
    font-size: 12px;
}

QSplitter::handle {
    background: #0f3460;
    width: 2px;
}
"""

CARD_STYLE = """
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 12px;
    padding: 16px;
"""

CARD_HEADER_STYLE = """
    font-size: 16px;
    font-weight: 600;
    color: #e0e0e0;
    padding: 4px 0;
"""

SIDEBAR_STYLE = """
    QWidget {
        background-color: #0f0f23;
    }
    QPushButton {
        background-color: transparent;
        color: #888;
        border: none;
        border-radius: 8px;
        padding: 14px 20px;
        text-align: left;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #16213e;
        color: #e0e0e0;
    }
    QPushButton:checked {
        background-color: #533483;
        color: #ffffff;
    }
"""

DASHBOARD_CARD_STYLE = """
    QFrame {
        background-color: #16213e;
        border: 1px solid #0f3460;
        border-radius: 12px;
    }
"""
