import os
import numpy as np
import cv2


class VideoModel:
    def __init__(self, path: str = ""):
        self.path = path
        self.cap = None
        self.fps: float = 0.0
        self.total_frames: int = 0
        self.width: int = 0
        self.height: int = 0
        self.duration: float = 0.0
        self.codec: str = ""
        self.file_size: int = 0
        self.frames: list[np.ndarray] = []
        self.original_audio_path: str = ""

    def load(self, path: str) -> bool:
        self.path = path
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            return False
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.duration = self.total_frames / self.fps if self.fps > 0 else 0.0
        codec_int = int(self.cap.get(cv2.CAP_PROP_FOURCC))
        self.codec = "".join(chr((codec_int >> 8 * i) & 0xFF) for i in range(4))
        self.file_size = os.path.getsize(path) if os.path.exists(path) else 0
        self.frames = []
        return True

    def read_frames(self) -> list[np.ndarray]:
        if not self.cap:
            return []
        self.frames = []
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            self.frames.append(frame)
        self.cap.release()
        self.cap = None
        return self.frames

    def get_frame_array(self) -> np.ndarray:
        if not self.frames:
            return np.array([])
        return np.array(self.frames)

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None

    def get_info(self) -> dict:
        return {
            "path": self.path,
            "fps": self.fps,
            "total_frames": self.total_frames,
            "width": self.width,
            "height": self.height,
            "resolution": f"{self.width}x{self.height}",
            "duration": self.duration,
            "codec": self.codec,
            "file_size": self.file_size,
            "file_size_str": self._format_size(self.file_size),
        }

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
