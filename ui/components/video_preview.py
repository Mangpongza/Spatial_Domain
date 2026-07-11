import cv2
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider, QScrollArea
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap


class VideoPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.playing = False
        self.current_frame_idx = 0
        self.total_frames = 0
        self.frames = []
        self.zoom_factor = 1.0

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.header = QLabel("Video Preview")
        self.header.setStyleSheet("font-size: 14px; font-weight: 600; color: #e0e0e0;")

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: 1px solid #0f3460; border-radius: 8px; background-color: #000;")

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(320, 240)
        self.video_label.setStyleSheet("background-color: #000;")
        self.video_label.setText("No video loaded")
        self.video_label.setStyleSheet("color: #666; font-size: 16px;")

        self.scroll.setWidget(self.video_label)

        controls = QHBoxLayout()
        self.play_btn = QPushButton("Play")
        self.play_btn.setFixedWidth(80)
        self.play_btn.clicked.connect(self.toggle_play)

        self.frame_slider = QSlider(Qt.Orientation.Horizontal)
        self.frame_slider.setMinimum(0)
        self.frame_slider.valueChanged.connect(self.slider_changed)

        self.frame_label = QLabel("0 / 0")
        self.frame_label.setFixedWidth(80)

        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setFixedWidth(36)
        self.zoom_in_btn.clicked.connect(self.zoom_in)

        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.setFixedWidth(36)
        self.zoom_out_btn.clicked.connect(self.zoom_out)

        controls.addWidget(self.play_btn)
        controls.addWidget(self.frame_slider)
        controls.addWidget(self.frame_label)
        controls.addWidget(self.zoom_in_btn)
        controls.addWidget(self.zoom_out_btn)

        layout.addWidget(self.header)
        layout.addWidget(self.scroll, 1)
        layout.addLayout(controls)

    def load_frames(self, frames: list[np.ndarray]):
        self.frames = frames
        self.total_frames = len(frames)
        self.current_frame_idx = 0
        self.frame_slider.setMaximum(max(0, self.total_frames - 1))
        if self.frames:
            self.show_frame(0)
        self.frame_label.setText(f"0 / {self.total_frames}")

    def load_video(self, path: str):
        self.cap = cv2.VideoCapture(path)
        if self.cap.isOpened():
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.frame_slider.setMaximum(max(0, self.total_frames - 1))
            self.frame_label.setText(f"0 / {self.total_frames}")
            self.next_frame()

    def show_frame(self, idx: int):
        if 0 <= idx < len(self.frames):
            frame = self.frames[idx]
            h, w = frame.shape[:2]
            new_w = int(w * self.zoom_factor)
            new_h = int(h * self.zoom_factor)
            frame = cv2.resize(frame, (new_w, new_h))
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = rgb.shape[:2]
            qimg = QImage(rgb.data, w, h, w * 3, QImage.Format.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qimg))
            self.current_frame_idx = idx
            self.frame_label.setText(f"{idx + 1} / {self.total_frames}")

    def next_frame(self):
        if self.frames and self.playing:
            idx = (self.current_frame_idx + 1) % self.total_frames
            self.frame_slider.setValue(idx)
            self.show_frame(idx)

    def toggle_play(self):
        self.playing = not self.playing
        self.play_btn.setText("Pause" if self.playing else "Play")
        if self.playing:
            self.timer.start(33)
        else:
            self.timer.stop()

    def slider_changed(self, value: int):
        if not self.playing:
            self.show_frame(value)

    def zoom_in(self):
        self.zoom_factor = min(4.0, self.zoom_factor * 1.25)
        if self.frames:
            self.show_frame(self.current_frame_idx)

    def zoom_out(self):
        self.zoom_factor = max(0.25, self.zoom_factor * 0.8)
        if self.frames:
            self.show_frame(self.current_frame_idx)

    def clear(self):
        self.frames = []
        self.total_frames = 0
        self.current_frame_idx = 0
        self.video_label.clear()
        self.video_label.setText("No video loaded")
        self.frame_slider.setMaximum(0)
        self.frame_label.setText("0 / 0")
        self.playing = False
        self.play_btn.setText("Play")
        self.timer.stop()
