import os
import struct
import numpy as np


class AudioModel:
    def __init__(self, path: str = ""):
        self.path = path
        self.sample_rate: int = 0
        self.channels: int = 0
        self.bit_depth: int = 16
        self.duration: float = 0.0
        self.file_size: int = 0
        self.data: bytes = b""
        self.format_id: int = 0

    def load(self, path: str) -> bool:
        self.path = path
        self.file_size = os.path.getsize(path) if os.path.exists(path) else 0
        ext = os.path.splitext(path)[1].lower()
        if ext == ".wav":
            return self._load_wav(path)
        elif ext == ".mp3":
            return self._load_mp3(path)
        return False

    def _load_wav(self, path: str) -> bool:
        try:
            with open(path, "rb") as f:
                header = f.read(44)
                if header[:4] != b"RIFF" or header[8:12] != b"WAVE":
                    return False
                self.channels = struct.unpack("<H", header[22:24])[0]
                self.sample_rate = struct.unpack("<I", header[24:28])[0]
                self.bit_depth = struct.unpack("<H", header[34:36])[0]
                data_size = struct.unpack("<I", header[40:44])[0]
                self.data = header + f.read(data_size)
                self.duration = data_size / (self.sample_rate * self.channels * (self.bit_depth // 8))
                self.format_id = 1
                return True
        except Exception:
            return False

    def _load_mp3(self, path: str) -> bool:
        try:
            with open(path, "rb") as f:
                self.data = f.read()
            self.sample_rate = 44100
            self.channels = 2
            self.bit_depth = 16
            self.duration = self.file_size / (128 * 1024 / 8)
            self.format_id = 2
            return True
        except Exception:
            return False

    def get_info(self) -> dict:
        return {
            "path": self.path,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "bit_depth": self.bit_depth,
            "duration": self.duration,
            "file_size": self.file_size,
            "file_size_str": self._format_size(self.file_size),
            "format_id": self.format_id,
        }

    def get_raw_bytes(self) -> bytes:
        return self.data

    @staticmethod
    def _format_size(size: int) -> str:
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 ** 3:
            return f"{size / 1024 ** 2:.2f} MB"
        else:
            return f"{size / 1024 ** 3:.2f} GB"
