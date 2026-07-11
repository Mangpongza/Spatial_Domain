from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QFileDialog, QScrollArea, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
import numpy as np
import cv2
import os
import time

from ui.components.drag_drop import DragDropWidget
from ui.components.log_console import LogConsole
from ui.components.progress_bar import StyledProgressBar
from ui.components.video_preview import VideoPreview
from analysis.metrics import MetricsAnalyzer
from algorithms import get_algorithm
from utils.logging import log_emitter
from skimage.metrics import structural_similarity as ssim


class AnalysisPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_frames = None
        self.stego_frames = None
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

        header = QLabel("วิเคราะห์ผล")
        header.setStyleSheet("font-size: 28px; font-weight: 700; color: #e0e0e0;")
        layout.addWidget(header)

        input_section = QHBoxLayout()
        orig_group = QGroupBox("วิดีโอต้นฉบับ")
        orig_layout = QVBoxLayout(orig_group)
        self.orig_drop = DragDropWidget("วางวิดีโอต้นฉบับ")
        self.orig_drop.file_dropped.connect(self.on_original_dropped)
        self.orig_path_label = QLabel("ยังไม่ได้เลือกไฟล์")
        self.orig_path_label.setStyleSheet("color: #888;")
        self.orig_browse = QPushButton("เลือกไฟล์")
        self.orig_browse.clicked.connect(lambda: self.browse_video(True))
        orig_layout.addWidget(self.orig_drop)
        orig_layout.addWidget(self.orig_path_label)
        orig_layout.addWidget(self.orig_browse)
        input_section.addWidget(orig_group)

        stego_group = QGroupBox("วิดีโอที่ฝังข้อมูลแล้ว")
        stego_layout = QVBoxLayout(stego_group)
        self.stego_drop = DragDropWidget("วางวิดีโอที่ฝังข้อมูลแล้ว")
        self.stego_drop.file_dropped.connect(self.on_stego_dropped)
        self.stego_path_label = QLabel("ยังไม่ได้เลือกไฟล์")
        self.stego_path_label.setStyleSheet("color: #888;")
        self.stego_browse = QPushButton("เลือกไฟล์")
        self.stego_browse.clicked.connect(lambda: self.browse_video(False))
        stego_layout.addWidget(self.stego_drop)
        stego_layout.addWidget(self.stego_path_label)
        stego_layout.addWidget(self.stego_browse)
        input_section.addWidget(stego_group)
        layout.addLayout(input_section)

        btn_row = QHBoxLayout()
        self.analyze_btn = QPushButton("วิเคราะห์")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #533483; color: white; font-size: 16px;
                font-weight: 600; padding: 12px 28px; border-radius: 10px;
            }
            QPushButton:hover { background-color: #7b5ea7; }
            QPushButton:disabled { background-color: #333; color: #666; }
        """)
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setEnabled(False)
        btn_row.addWidget(self.analyze_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        results_group = QGroupBox("ผลการวิเคราะห์")
        results_layout = QVBoxLayout(results_group)
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["ค่า", "ผลลัพธ์"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setAlternatingRowColors(True)
        results_layout.addWidget(self.results_table)
        layout.addWidget(results_group)

        self.progress_bar = StyledProgressBar()
        layout.addWidget(self.progress_bar)

        self.log_console = LogConsole()
        layout.addWidget(self.log_console)

        scroll.setWidget(container)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def browse_video(self, is_original: bool):
        path, _ = QFileDialog.getOpenFileName(
            self, "เลือกวิดีโอ", "",
            "วิดีโอ (*.mp4 *.mkv *.avi *.mov);;ไฟล์ทั้งหมด (*)"
        )
        if path:
            if is_original:
                self.on_original_dropped(path)
            else:
                self.on_stego_dropped(path)

    def on_original_dropped(self, path: str):
        self.orig_path_label.setText(os.path.basename(path))
        self.orig_drop.set_text(os.path.basename(path))
        self._load_frames(path, True)

    def on_stego_dropped(self, path: str):
        self.stego_path_label.setText(os.path.basename(path))
        self.stego_drop.set_text(os.path.basename(path))
        self._load_frames(path, False)

    def _load_frames(self, path: str, is_original: bool):
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            log_emitter.emit(f"Failed to open: {path}")
            return
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()
        if is_original:
            self.original_frames = np.array(frames)
            log_emitter.emit(f"Loaded {len(frames)} original frames")
        else:
            self.stego_frames = np.array(frames)
            log_emitter.emit(f"Loaded {len(frames)} stego frames")
        self.analyze_btn.setEnabled(
            self.original_frames is not None and self.stego_frames is not None
        )

    def start_analysis(self):
        if self.original_frames is None or self.stego_frames is None:
            return
        self.progress_bar.setValue(10)
        log_emitter.emit("Starting analysis...")
        try:
            min_frames = min(len(self.original_frames), len(self.stego_frames))
            orig = self.original_frames[:min_frames]
            stego = self.stego_frames[:min_frames]

            analyzer = MetricsAnalyzer()
            diff = orig.astype(np.int16) - stego.astype(np.int16)
            mse = float(np.mean(diff ** 2))
            psnr = float('inf') if mse == 0 else float(20 * np.log10(255.0 / np.sqrt(mse)))

            orig_gray = np.mean(orig.astype(np.float32), axis=3)
            stego_gray = np.mean(stego.astype(np.float32), axis=3)
            ssim_val = float(ssim(
                orig_gray,
                stego_gray,
                data_range=255, win_size=3, channel_axis=None,
            ))

            ber = float(np.sum(diff != 0)) / diff.size if diff.size > 0 else 0.0

            capacity = orig[0].shape[0] * orig[0].shape[1] // 8 * min_frames
            payload_size = int(np.sum(diff != 0) // 8)

            metrics = {
                "PSNR (dB)": f"{psnr:.4f}",
                "SSIM": f"{ssim_val:.6f}",
                "MSE": f"{mse:.6f}",
                "อัตราความผิดพลาด (BER)": f"{ber:.6f}",
                "จำนวนเฟรม": str(min_frames),
                "ความละเอียด": f"{orig[0].shape[1]}x{orig[0].shape[0]}",
                "ความจุข้อมูล (ไบต์)": str(capacity),
                "ขนาดข้อมูลที่ฝังโดยประมาณ (ไบต์)": str(payload_size),
                "อัตราการใช้พื้นที่ (%)": f"{(payload_size / capacity * 100) if capacity > 0 else 0:.2f}",
            }

            self.progress_bar.setValue(80)
            self.results_table.setRowCount(len(metrics))
            for row, (key, val) in enumerate(metrics.items()):
                self.results_table.setItem(row, 0, QTableWidgetItem(key))
                self.results_table.setItem(row, 1, QTableWidgetItem(val))

            self.progress_bar.setValue(100)
            log_emitter.emit("Analysis completed!")

        except Exception as e:
            log_emitter.emit(f"Analysis failed: {str(e)}")
