from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QColor, QTextCursor


class LogConsole(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumHeight(200)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a1a;
                color: #00ff88;
                border: 1px solid #0f3460;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)

    @pyqtSlot(str)
    def append_message(self, message: str):
        color = "#00ff88"
        if "Failed" in message or "failed" in message or "Error" in message or "error" in message:
            color = "#ff4444"
        elif "Completed" in message or "completed" in message or "Success" in message:
            color = "#44ff44"
        elif "Found" in message or "Verified" in message or "Detected" in message:
            color = "#ffaa00"
        elif "Trying" in message:
            color = "#8888ff"
        self.append(f'<span style="color: {color};">{message}</span>')
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
