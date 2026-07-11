from PyQt6.QtCore import QObject, pyqtSignal


class MainController(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_connections()

    def setup_connections(self):
        embed_page = self.main_window.get_page("embed")
        extract_page = self.main_window.get_page("extract")
        analysis_page = self.main_window.get_page("analysis")
        benchmark_page = self.main_window.get_page("benchmark")

        embed_page.navigation_request.connect(self.main_window.navigate_to)
