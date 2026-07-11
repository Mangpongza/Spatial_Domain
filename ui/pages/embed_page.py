import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QFormLayout, QFileDialog,
    QFrame, QGridLayout, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

from ui.components.drag_drop import DragDropWidget
from ui.components.log_console import LogConsole
from ui.components.progress_bar import StyledProgressBar
from models.video_model import VideoModel
from models.audio_model import AudioModel
from utils.constants import ALGORITHM_NAMES, SUPPORTED_VIDEO_EXTENSIONS, SUPPORTED_AUDIO_EXTENSIONS
from utils.logging import log_emitter
from services.embedding_service import EmbedWorker


class EmbedPage(QWidget):
    navigation_request = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_model = None
        self.audio_model = None
        self.video_service = None
        self.embed_worker = None
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

        header = QLabel("ฝังเสียง")
        header.setStyleSheet("font-size: 28px; font-weight: 700; color: #e0e0e0;")
        layout.addWidget(header)

        input_section = QHBoxLayout()
        input_section.setSpacing(16)

        video_group = QGroupBox("วิดีโอต้นทาง")
        video_layout = QVBoxLayout(video_group)
        self.video_drop = DragDropWidget("วางวิดีโอที่นี่\nMP4, MKV, AVI, MOV")
        self.video_drop.file_dropped.connect(self.on_video_dropped)
        self.video_path_label = QLabel("ยังไม่ได้เลือกวิดีโอ")
        self.video_path_label.setStyleSheet("color: #888; font-size: 12px;")
        self.video_browse_btn = QPushButton("เลือกวิดีโอ")
        self.video_browse_btn.clicked.connect(self.browse_video)
        video_layout.addWidget(self.video_drop)
        video_layout.addWidget(self.video_path_label)
        video_layout.addWidget(self.video_browse_btn)
        input_section.addWidget(video_group)

        audio_group = QGroupBox("เสียงต้นทาง")
        audio_layout = QVBoxLayout(audio_group)
        self.audio_drop = DragDropWidget("วางเสียงที่นี่\nWAV, MP3")
        self.audio_drop.file_dropped.connect(self.on_audio_dropped)
        self.audio_path_label = QLabel("ยังไม่ได้เลือกเสียง")
        self.audio_path_label.setStyleSheet("color: #888; font-size: 12px;")
        self.audio_browse_btn = QPushButton("เลือกเสียง")
        self.audio_browse_btn.clicked.connect(self.browse_audio)
        audio_layout.addWidget(self.audio_drop)
        audio_layout.addWidget(self.audio_path_label)
        audio_layout.addWidget(self.audio_browse_btn)
        input_section.addWidget(audio_group)

        layout.addLayout(input_section)

        info_section = QHBoxLayout()
        self.video_info_group = QGroupBox("ข้อมูลวิดีโอ")
        self.video_info_layout = QFormLayout(self.video_info_group)
        self.video_info_widgets = {}
        for key, label in [
            ("resolution", "ความละเอียด"), ("fps", "เฟรมต่อวินาที"), ("duration", "ระยะเวลา"),
            ("codec", "โคเดก"), ("total_frames", "จำนวนเฟรม"), ("file_size", "ขนาดไฟล์"),
        ]:
            lbl = QLabel("--")
            lbl.setStyleSheet("color: #ccc;")
            self.video_info_layout.addRow(f"{label}:", lbl)
            self.video_info_widgets[key] = lbl
        info_section.addWidget(self.video_info_group)

        self.audio_info_group = QGroupBox("ข้อมูลเสียง")
        self.audio_info_layout = QFormLayout(self.audio_info_group)
        self.audio_info_widgets = {}
        for key, label in [
            ("sample_rate", "อัตราสุ่ม"), ("channels", "ช่องสัญญาณ"),
            ("bit_depth", "ความลึกบิต"), ("duration", "ระยะเวลา"), ("file_size", "ขนาดไฟล์"),
        ]:
            lbl = QLabel("--")
            lbl.setStyleSheet("color: #ccc;")
            self.audio_info_layout.addRow(f"{label}:", lbl)
            self.audio_info_widgets[key] = lbl
        info_section.addWidget(self.audio_info_group)
        layout.addLayout(info_section)

        algo_group = QGroupBox("เลือกอัลกอริทึม")
        algo_layout = QVBoxLayout(algo_group)
        algo_row = QHBoxLayout()

        self.algo_combo = QComboBox()
        self.algo_combo.addItem("Standard LSB 1-Bit", 0)
        self.algo_combo.addItem("Standard LSB 2-Bit", 1)
        self.algo_combo.addItem("Standard LSB 3-Bit", 2)
        self.algo_combo.addItem("Random LSB", 3)
        self.algo_combo.addItem("Adaptive LSB", 4)
        self.algo_combo.addItem("Edge-Based LSB", 5)
        self.algo_combo.addItem("LSBM", 6)
        self.algo_combo.addItem("LSBMR", 7)
        self.algo_combo.addItem("PVD", 8)
        self.algo_combo.addItem("BPCS", 9)
        self.algo_combo.addItem("OPAP", 10)
        self.algo_combo.addItem("PIT", 11)
        self.algo_combo.setMinimumWidth(200)

        algo_row.addWidget(QLabel("อัลกอริทึม:"))
        algo_row.addWidget(self.algo_combo)
        algo_row.addStretch()
        algo_layout.addLayout(algo_row)

        self.embed_btn = QPushButton("เริ่มฝังข้อมูล")
        self.embed_btn.setStyleSheet("""
            QPushButton {
                background-color: #533483;
                color: white;
                font-size: 16px;
                font-weight: 600;
                padding: 14px 32px;
                border-radius: 10px;
            }
            QPushButton:hover { background-color: #7b5ea7; }
            QPushButton:disabled { background-color: #333; color: #666; }
        """)
        self.embed_btn.clicked.connect(self.start_embedding)
        self.embed_btn.setEnabled(False)
        algo_layout.addWidget(self.embed_btn)
        layout.addWidget(algo_group)

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
            self, "Select Video",
            "",
            "Video Files (*.mp4 *.mkv *.avi *.mov);;All Files (*)"
        )
        if path:
            self.on_video_dropped(path)

    def browse_audio(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio",
            "",
            "Audio Files (*.wav *.mp3);;All Files (*)"
        )
        if path:
            self.on_audio_dropped(path)

    def on_video_dropped(self, path: str):
        ext = os.path.splitext(path)[1].lower()
        if ext not in SUPPORTED_VIDEO_EXTENSIONS:
            log_emitter.emit(f"Unsupported video format: {ext}")
            return
        try:
            self.video_model = VideoModel()
            if self.video_model.load(path):
                self.video_path_label.setText(os.path.basename(path))
                self.video_drop.set_text(os.path.basename(path))
                info = self.video_model.get_info()
                self.video_info_widgets["resolution"].setText(info["resolution"])
                self.video_info_widgets["fps"].setText(f"{info['fps']:.2f}")
                self.video_info_widgets["duration"].setText(f"{info['duration']:.2f}s")
                self.video_info_widgets["codec"].setText(info["codec"])
                self.video_info_widgets["total_frames"].setText(str(info["total_frames"]))
                self.video_info_widgets["file_size"].setText(info["file_size_str"])
                log_emitter.emit(f"Loaded video: {os.path.basename(path)}")
                self.update_embed_button()
            else:
                log_emitter.emit(f"Failed to load video: {path}")
        except Exception as e:
            log_emitter.emit(f"Error loading video: {str(e)}")

    def on_audio_dropped(self, path: str):
        ext = os.path.splitext(path)[1].lower()
        if ext not in SUPPORTED_AUDIO_EXTENSIONS:
            log_emitter.emit(f"Unsupported audio format: {ext}")
            return
        try:
            self.audio_model = AudioModel()
            if self.audio_model.load(path):
                self.audio_path_label.setText(os.path.basename(path))
                self.audio_drop.set_text(os.path.basename(path))
                info = self.audio_model.get_info()
                self.audio_info_widgets["sample_rate"].setText(f"{info['sample_rate']} Hz")
                self.audio_info_widgets["channels"].setText(str(info["channels"]))
                self.audio_info_widgets["bit_depth"].setText(f"{info['bit_depth']}-bit")
                self.audio_info_widgets["duration"].setText(f"{info['duration']:.2f}s")
                self.audio_info_widgets["file_size"].setText(info["file_size_str"])
                log_emitter.emit(f"Loaded audio: {os.path.basename(path)}")
                self.update_embed_button()
            else:
                log_emitter.emit(f"Failed to load audio: {path}")
        except Exception as e:
            log_emitter.emit(f"Error loading audio: {str(e)}")

    def update_embed_button(self):
        self.embed_btn.setEnabled(
            self.video_model is not None and self.audio_model is not None
        )

    def start_embedding(self):
        if not self.video_model or not self.audio_model:
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self, "บันทึกวิดีโอที่ฝังข้อมูลแล้ว",
            "outputs/stego_video.mp4",
            "วิดีโอ (*.mp4);;ไฟล์ทั้งหมด (*)"
        )
        if not output_path:
            return

        algo_id = self.algo_combo.currentData()
        self.embed_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_console.clear()

        self.embed_worker = EmbedWorker(
            video_path=self.video_model.path,
            audio_path=self.audio_model.path,
            output_path=output_path,
            algorithm_id=algo_id,
            lsb_mode=1,
        )
        self.embed_worker.progress.connect(self.progress_bar.setValue)
        self.embed_worker.finished.connect(self.on_embed_finished)
        self.embed_worker.error.connect(self.on_embed_error)
        self.embed_worker.start()

    @pyqtSlot(str)
    def on_embed_finished(self, path: str):
        log_emitter.emit(f"Stego video saved to: {path}")
        self.embed_btn.setEnabled(True)

    @pyqtSlot(str)
    def on_embed_error(self, error: str):
        self.embed_btn.setEnabled(True)
