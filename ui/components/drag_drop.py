from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent


class DragDropWidget(QWidget):
    file_dropped = pyqtSignal(str)

    def __init__(self, label_text: str = "Drag & Drop file here", parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)
        self.setStyleSheet("""
            QWidget {
                border: 2px dashed #0f3460;
                border-radius: 12px;
                background-color: #16213e;
            }
            QWidget:hover {
                border-color: #533483;
                background-color: #1a1a2e;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel(label_text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 16px; color: #888; border: none; background: transparent;")
        layout.addWidget(self.label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QWidget {
                    border: 2px dashed #533483;
                    border-radius: 12px;
                    background-color: #1a1a2e;
                }
            """)

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QWidget {
                border: 2px dashed #0f3460;
                border-radius: 12px;
                background-color: #16213e;
            }
            QWidget:hover {
                border-color: #533483;
                background-color: #1a1a2e;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path:
                    self.file_dropped.emit(file_path)
                    break
        self.dragLeaveEvent(event)

    def set_text(self, text: str):
        self.label.setText(text)
