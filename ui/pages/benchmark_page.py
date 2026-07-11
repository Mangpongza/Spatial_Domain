from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFileDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSlot
import numpy as np
import cv2
import os

from ui.components.log_console import LogConsole
from ui.components.progress_bar import StyledProgressBar
from benchmark import BenchmarkRunner
from utils.logging import log_emitter


class BenchmarkPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frames = None
        self.benchmark_runner = None
        self.results = []
        self.setup_ui()
        log_emitter.message.connect(self.log_console.append_message)

    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("Benchmark")
        header.setStyleSheet("font-size: 28px; font-weight: 700; color: #e0e0e0;")
        layout.addWidget(header)

        video_group = QGroupBox("Test Video")
        video_layout = QHBoxLayout(video_group)
        self.video_label = QLabel("No video selected")
        self.video_label.setStyleSheet("color: #888;")
        self.browse_btn = QPushButton("Browse Video")
        self.browse_btn.clicked.connect(self.browse_video)
        video_layout.addWidget(self.video_label, 1)
        video_layout.addWidget(self.browse_btn)
        layout.addWidget(video_group)

        controls = QHBoxLayout()
        self.payload_size_input = QLabel("Payload size: 1024 bytes")
        self.payload_size_input.setStyleSheet("color: #ccc;")
        self.run_btn = QPushButton("Run Benchmark")
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #533483; color: white; font-size: 16px;
                font-weight: 600; padding: 12px 28px; border-radius: 10px;
            }
            QPushButton:hover { background-color: #7b5ea7; }
            QPushButton:disabled { background-color: #333; color: #666; }
        """)
        self.run_btn.clicked.connect(self.run_benchmark)
        self.run_btn.setEnabled(False)
        controls.addWidget(self.payload_size_input)
        controls.addStretch()
        controls.addWidget(self.run_btn)
        layout.addLayout(controls)

        self.progress_bar = StyledProgressBar()
        layout.addWidget(self.progress_bar)

        results_group = QGroupBox("Benchmark Results")
        results_layout = QVBoxLayout(results_group)
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(9)
        self.results_table.setHorizontalHeaderLabels([
            "Algorithm", "Embed Speed (B/s)", "Extract Speed (B/s)",
            "Embed Time (s)", "Extract Time (s)", "PSNR (dB)",
            "MSE", "BER", "Capacity (B)"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.setAlternatingRowColors(True)
        results_layout.addWidget(self.results_table)
        layout.addWidget(results_group)

        self.log_console = LogConsole()
        layout.addWidget(self.log_console)

        scroll.setWidget(container)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def browse_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Test Video", "",
            "Video Files (*.mp4 *.mkv *.avi *.mov);;All Files (*)"
        )
        if path:
            self.video_label.setText(os.path.basename(path))
            cap = cv2.VideoCapture(path)
            frames = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
                if len(frames) >= 30:
                    break
            cap.release()
            if frames:
                self.frames = np.array(frames)
                log_emitter.emit(f"Loaded {len(frames)} frames for benchmark")
                self.run_btn.setEnabled(True)

    def run_benchmark(self):
        if self.frames is None:
            return
        self.run_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.results_table.setRowCount(0)
        self.results = []

        self.benchmark_runner = BenchmarkRunner(self.frames, payload_size=1024)
        self.benchmark_runner.progress.connect(self._on_progress)
        self.benchmark_runner.result_ready.connect(self._on_result)
        self.benchmark_runner.finished.connect(self._on_finished)
        self.benchmark_runner.start()

    @pyqtSlot(int, int)
    def _on_progress(self, current: int, total: int):
        self.progress_bar.setValue(int(current / total * 100))

    @pyqtSlot(int, dict)
    def _on_result(self, algo_id: int, result: dict):
        self.results.append(result)
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        self.results_table.setItem(row, 0, QTableWidgetItem(result.get("algorithm_name", "")))
        self.results_table.setItem(row, 1, QTableWidgetItem(f"{result.get('embedding_speed', 0):.2f}"))
        self.results_table.setItem(row, 2, QTableWidgetItem(f"{result.get('extraction_speed', 0):.2f}"))
        self.results_table.setItem(row, 3, QTableWidgetItem(f"{result.get('embedding_time', 0):.6f}"))
        self.results_table.setItem(row, 4, QTableWidgetItem(f"{result.get('extraction_time', 0):.6f}"))
        self.results_table.setItem(row, 5, QTableWidgetItem(f"{result.get('psnr', 0):.4f}"))
        self.results_table.setItem(row, 6, QTableWidgetItem(f"{result.get('mse', 0):.6f}"))
        self.results_table.setItem(row, 7, QTableWidgetItem(f"{result.get('ber', 0):.6f}"))
        self.results_table.setItem(row, 8, QTableWidgetItem(str(result.get('payload_capacity', 0))))

    @pyqtSlot(list)
    def _on_finished(self, results: list):
        log_emitter.emit("Benchmark completed! All algorithms tested.")
        self.run_btn.setEnabled(True)
