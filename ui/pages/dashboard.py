from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt


class StatCard(QFrame):
    def __init__(self, title: str, value: str, icon: str = "", color: str = "#533483"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 12px;
                padding: 16px;
                border-left: 4px solid {color};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 12px; color: #888; border: none; background: transparent;")

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {color}; border: none; background: transparent;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("หน้าแรก")
        header.setStyleSheet("font-size: 28px; font-weight: 700; color: #e0e0e0;")
        layout.addWidget(header)

        subtitle = QLabel("เครื่องมือซ่อนข้อมูลเสียงในวิดีโอ")
        subtitle.setStyleSheet("font-size: 14px; color: #888; margin-top: -12px;")
        layout.addWidget(subtitle)

        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)

        self.cards = {
            "algorithms": StatCard("อัลกอริทึมที่รองรับ", "5 วิธี", color="#533483"),
            "methods": StatCard("วิธีการฝัง", "Standard LSB 1/2/3-Bit / Random LSB / Adaptive LSB", color="#0f3460"),
            "detection": StatCard("การตรวจจับ", "ตรวจจับอัลกอริทึมอัตโนมัติ", color="#00cc88"),
            "formats": StatCard("รูปแบบที่รองรับ", "วิดีโอ: MP4, MKV, AVI, MOV\nเสียง: WAV, MP3", color="#ffaa00"),
        }
        stats_grid.addWidget(self.cards["algorithms"], 0, 0)
        stats_grid.addWidget(self.cards["formats"], 0, 1)
        stats_grid.addWidget(self.cards["detection"], 1, 0)
        stats_grid.addWidget(self.cards["methods"], 1, 1)

        layout.addLayout(stats_grid)

        features_header = QLabel("ความสามารถ")
        features_header.setStyleSheet("font-size: 18px; font-weight: 600; color: #e0e0e0; margin-top: 8px;")
        layout.addWidget(features_header)

        features = [
            "ฝังไฟล์เสียง (WAV/MP3) ลงในวิดีโอ (MP4/MKV/AVI/MOV)",
            "รองรับอัลกอริทึมซ่อนข้อมูลหลายรูปแบบ",
            "ตรวจจับอัลกอริทึมที่ใช้อัตโนมัติตอนถอนข้อมูล",
            "วิเคราะห์ผลด้วย PSNR, SSIM, MSE, BER",
            "ทดสอบเปรียบเทียบทุกอัลกอริทึมพร้อมกราฟ",
            "อินเทอร์เฟซ Material Design โทนสีเข้ม",
            "รองรับการลากวางไฟล์ (Drag & Drop)",
            "แสดงบันทึกการทำงานแบบเรียลไทม์",
        ]
        for feat in features:
            lbl = QLabel(f"  {feat}")
            lbl.setStyleSheet("font-size: 13px; color: #ccc; padding: 3px 0;")
            layout.addWidget(lbl)

        layout.addStretch()
