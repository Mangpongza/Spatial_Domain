from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QCheckBox, QSpinBox, QComboBox,
    QScrollArea,
)
from PyQt6.QtCore import Qt

from utils.logging import log_emitter


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("ตั้งค่า")
        header.setStyleSheet("font-size: 28px; font-weight: 700; color: #e0e0e0;")
        layout.addWidget(header)

        general_group = QGroupBox("ทั่วไป")
        general_layout = QFormLayout(general_group)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["โหมดมืด (ค่าเริ่มต้น)", "โหมดสว่าง"])
        self.theme_combo.setCurrentIndex(0)
        general_layout.addRow("ธีม:", self.theme_combo)

        self.save_outputs = QCheckBox("บันทึกผลลัพธ์ในโฟลเดอร์ outputs/")
        self.save_outputs.setChecked(True)
        general_layout.addRow("", self.save_outputs)

        self.auto_clear = QCheckBox("ล้างบันทึกอัตโนมัติเมื่อเริ่มทำงานใหม่")
        self.auto_clear.setChecked(True)
        general_layout.addRow("", self.auto_clear)
        layout.addWidget(general_group)

        algo_group = QGroupBox("ค่าพื้นฐานอัลกอริทึม")
        algo_layout = QFormLayout(algo_group)
        self.default_algo = QComboBox()
        self.default_algo.addItems([
            "Standard LSB 1-Bit", "Standard LSB 2-Bit", "Standard LSB 3-Bit",
            "Random LSB", "Adaptive LSB", "Edge-Based LSB",
            "LSBM", "LSBMR", "PVD", "BPCS", "OPAP", "PIT"
        ])
        algo_layout.addRow("อัลกอริทึมเริ่มต้น:", self.default_algo)
        layout.addWidget(algo_group)

        perf_group = QGroupBox("ประสิทธิภาพ")
        perf_layout = QFormLayout(perf_group)
        self.thread_count = QSpinBox()
        self.thread_count.setMinimum(1)
        self.thread_count.setMaximum(16)
        self.thread_count.setValue(4)
        perf_layout.addRow("จำนวนเธรด:", self.thread_count)

        self.cache_frames = QCheckBox("แคชเฟรมไว้ในหน่วยความจำ")
        self.cache_frames.setChecked(True)
        perf_layout.addRow("", self.cache_frames)
        layout.addWidget(perf_group)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("บันทึกการตั้งค่า")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #533483; color: white;
                font-weight: 600; padding: 12px 28px; border-radius: 10px;
            }
            QPushButton:hover { background-color: #7b5ea7; }
        """)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        layout.addStretch()

        scroll.setWidget(container)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)
