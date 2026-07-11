from PyQt6.QtCore import QObject, pyqtSignal


class LogEmitter(QObject):
    message = pyqtSignal(str)

    def emit(self, msg: str):
        self.message.emit(msg)


log_emitter = LogEmitter()


class LogPipe:
    PIPE = log_emitter
