from PyQt6.QtWidgets import QProgressBar


class StyledProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValue(0)
        self.setTextVisible(True)
        self.setMinimumHeight(22)
