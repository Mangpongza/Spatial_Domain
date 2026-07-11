import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QFileDialog, QScrollArea, QRadioButton,
    QButtonGroup,
)
from PyQt6.QtCore import Qt, pyqtSlot

from ui.components.drag_drop import DragDropWidget
from ui.components.log_console import LogConsole
from ui.components.progress_bar import StyledProgressBar
from utils.constants import ALGORITHM_NAMES
from utils.logging import log_emitter
from services.extraction_service import ExtractWorker


class ExtractPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.extract_worker = None
        self.video_path = ""
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

        header = QLabel("ถอนเสียง")
        header.setStyleSheet("font-size: 28px; font-weight: 700; color: #e0e0e0;")
        layout.addWidget(header)

        video_group = QGroupBox("วิดีโอที่ฝังข้อมูลแล้ว")
        video_layout = QVBoxLayout(video_group)
        self.video_drop = DragDropWidget("วางวิดีโอที่ฝังข้อมูลแล้วที่นี่\nMP4, MKV, AVI, MOV")
        self.video_drop.file_dropped.connect(self.on_video_dropped)
        self.video_path_label = QLabel("ยังไม่ได้เลือกวิดีโอ")
        self.video_path_label.setStyleSheet("color: #888; font-size: 12px;")
        self.video_browse_btn = QPushButton("เลือกวิดีโอ")
        self.video_browse_btn.clicked.connect(self.browse_video)
        video_layout.addWidget(self.video_drop)
        video_layout.addWidget(self.video_path_label)
        video_layout.addWidget(self.video_browse_btn)
        layout.addWidget(video_group)

        mode_group = QGroupBox("โหมดการถอนข้อมูล")
        mode_layout = QVBoxLayout(mode_group)
        self.mode_group = QButtonGroup(self)

        self.auto_radio = QRadioButton("ตรวจจับอัตโนมัติ")
        self.auto_radio.setChecked(True)
        self.manual_radio = QRadioButton("เลือกเอง")

        self.mode_group.addButton(self.auto_radio, 0)
        self.mode_group.addButton(self.manual_radio, 1)
        self.mode_group.buttonClicked.connect(self.on_mode_changed)

        mode_layout.addWidget(self.auto_radio)
        mode_layout.addWidget(self.manual_radio)

        self.manual_algo_layout = QHBoxLayout()
        self.manual_algo_layout.addWidget(QLabel("อัลกอริทึม:"))
        self.algo_combo = QComboBox()
        for algo_id, algo_name in sorted(ALGORITHM_NAMES.items()):
            self.algo_combo.addItem(algo_name, algo_id)
        self.algo_combo.setEnabled(False)
        self.manual_algo_layout.addWidget(self.algo_combo)
        self.manual_algo_layout.addStretch()
        mode_layout.addLayout(self.manual_algo_layout)
        layout.addWidget(mode_group)

        self.extract_btn = QPushButton("เริ่มถอนข้อมูล")
        self.extract_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f3460;
                color: white;
                font-size: 16px;
                font-weight: 600;
                padding: 14px 32px;
                border-radius: 10px;
            }
            QPushButton:hover { background-color: #1a4a8a; }
            QPushButton:disabled { background-color: #333; color: #666; }
        """)
        self.extract_btn.clicked.connect(self.start_extraction)
        self.extract_btn.setEnabled(False)
        layout.addWidget(self.extract_btn)

        self.progress_bar = StyledProgressBar()
        layout.addWidget(self.progress_bar)

        self.log_console = LogConsole()
        layout.addWidget(self.log_console)

        scroll.setWidget(container)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def browse_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Stego Video",
            "",
            "Video Files (*.mp4 *.mkv *.avi *.mov);;All Files (*)"
        )
        if path:
            self.on_video_dropped(path)

    def on_video_dropped(self, path: str):
        self.video_path = path
        self.video_path_label.setText(os.path.basename(path))
        self.video_drop.set_text(os.path.basename(path))
        self.extract_btn.setEnabled(True)
        log_emitter.emit(f"Loaded stego video: {os.path.basename(path)}")

    def on_mode_changed(self, btn):
        self.algo_combo.setEnabled(btn == self.manual_radio)

    def start_extraction(self):
        if not self.video_path:
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self, "บันทึกเสียงที่ถอนแล้ว",
            "outputs/extracted_audio.wav",
            "เสียง (*.wav *.mp3);;ไฟล์ทั้งหมด (*)"
        )
        if not output_path:
            return

        auto_detect = self.auto_radio.isChecked()
        algo_id = self.algo_combo.currentData() if not auto_detect else None

        self.extract_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_console.clear()

        self.extract_worker = ExtractWorker(
            video_path=self.video_path,
            output_path=output_path,
            algorithm_id=algo_id,
            auto_detect=auto_detect,
        )
        self.extract_worker.progress.connect(self.progress_bar.setValue)
        self.extract_worker.finished.connect(self.on_extract_finished)
        self.extract_worker.error.connect(self.on_extract_error)
        self.extract_worker.start()

    @pyqtSlot(str, dict)
    def on_extract_finished(self, path: str, info: dict):
        log_emitter.emit(f"Audio extracted to: {path}")
        log_emitter.emit(f"Detected: {info.get('algorithm_name', 'Unknown')}")
        log_emitter.emit(f"Payload size: {info.get('payload_size', 0)} bytes")
        self.extract_btn.setEnabled(True)

    @pyqtSlot(str)
    def on_extract_error(self, error: str):
        self.extract_btn.setEnabled(True)
