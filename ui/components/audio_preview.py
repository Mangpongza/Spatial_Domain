import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QImage, QPixmap


class WaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = np.array([], dtype=np.float32)
        self.setMinimumHeight(120)
        self.setStyleSheet("background-color: #0a0a1a; border: 1px solid #0f3460; border-radius: 8px;")

    def set_data(self, data: np.ndarray):
        self.data = data.astype(np.float32)
        self.update()

    def paintEvent(self, event):
        if len(self.data) < 2:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        painter.fillRect(0, 0, w, h, QColor(10, 10, 26))

        pen = QPen(QColor(83, 52, 131))
        pen.setWidth(1)
        painter.setPen(pen)

        center = h // 2
        step = max(1, len(self.data) // w)
        for x in range(w):
            idx = x * step
            if idx < len(self.data):
                val = self.data[idx] * (center - 8)
                val = max(-center + 4, min(center - 4, val))
                painter.drawLine(x, int(center - val), x, int(center + val))

        painter.end()


class AudioPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.audio_bytes = b""

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.header = QLabel("Audio Preview")
        self.header.setStyleSheet("font-size: 14px; font-weight: 600; color: #e0e0e0;")

        btn_layout = QHBoxLayout()
        self.play_btn = QPushButton("Play Original")
        self.play_btn.setEnabled(False)
        btn_layout.addWidget(self.play_btn)

        self.play_extracted_btn = QPushButton("Play Extracted")
        self.play_extracted_btn.setEnabled(False)
        btn_layout.addWidget(self.play_extracted_btn)

        self.waveform = WaveformWidget()

        self.spectrogram_label = QLabel()
        self.spectrogram_label.setMinimumHeight(100)
        self.spectrogram_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spectrogram_label.setStyleSheet("background-color: #0a0a1a; border: 1px solid #0f3460; border-radius: 8px; color: #666;")

        layout.addWidget(self.header)
        layout.addLayout(btn_layout)
        layout.addWidget(self.waveform, 2)
        layout.addWidget(self.spectrogram_label, 1)

    def load_audio(self, data: bytes, sample_rate: int = 44100):
        self.audio_bytes = data
        if len(data) > 44:
            samples = np.frombuffer(data[44:], dtype=np.int16).astype(np.float32)
            samples /= np.max(np.abs(samples)) + 1e-10
            self.waveform.set_data(samples[:min(len(samples), 44100 * 3)])
            self.play_btn.setEnabled(True)
            self.generate_spectrogram(samples, sample_rate)

    def generate_spectrogram(self, samples: np.ndarray, sample_rate: int):
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
            from matplotlib.figure import Figure

            fig = Figure(figsize=(4, 1.5))
            fig.patch.set_facecolor("#0a0a1a")
            ax = fig.add_subplot(111)
            ax.specgram(samples[:min(len(samples), sample_rate * 10)], Fs=sample_rate,
                        cmap="plasma", aspect="auto")
            ax.axis("off")
            fig.tight_layout(pad=0)
            canvas = FigureCanvas(fig)
            canvas.draw()
            buf = canvas.buffer_rgba()
            qimg = QImage(buf, canvas.width(), canvas.height(), QImage.Format.Format_RGBA8888)
            self.spectrogram_label.setPixmap(QPixmap.fromImage(qimg).scaled(
                self.spectrogram_label.width(), 100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            plt.close(fig)
        except Exception:
            self.spectrogram_label.setText("Spectrogram unavailable")

    def clear(self):
        self.audio_bytes = b""
        self.waveform.data = np.array([], dtype=np.float32)
        self.play_btn.setEnabled(False)
        self.play_extracted_btn.setEnabled(False)
        self.spectrogram_label.clear()
        self.spectrogram_label.setText("No audio loaded")
        self.update()
