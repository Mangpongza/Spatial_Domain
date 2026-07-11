import os
import time
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from services.video_service import VideoService
from services.audio_service import AudioService
from algorithms import get_algorithm
from utils.header import parse_header, HEADER_SIZE
from utils.constants import ALGORITHM_NAMES, AUTO_DETECTION_ORDER
from utils.logging import log_emitter


class ExtractWorker(QThread):
    finished = pyqtSignal(str, dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    log = pyqtSignal(str)

    def __init__(
        self,
        video_path: str,
        output_path: str,
        algorithm_id: int = None,
        auto_detect: bool = True,
    ):
        super().__init__()
        self.video_path = video_path
        self.output_path = output_path
        self.algorithm_id = algorithm_id
        self.auto_detect = auto_detect

    def run(self):
        try:
            self.progress.emit(5)
            log_emitter.emit("Starting extraction process...")

            video_service = VideoService()
            audio_service = AudioService()

            video_model = video_service.open(self.video_path)

            self.progress.emit(20)
            frames_array = video_service.read_all_frames(video_model)

            self.progress.emit(30)
            algo_ids = (
                [self.algorithm_id]
                if not self.auto_detect
                else AUTO_DETECTION_ORDER
            )

            detected_algo_id = None
            header_info = None
            payload = None

            for aid in algo_ids:
                name = ALGORITHM_NAMES.get(aid, f"Unknown ({aid})")
                log_emitter.emit(f"Trying {name}...")

                algo_class = get_algorithm(aid)
                if aid in (0, 1, 2):
                    bits = {0: 1, 1: 2, 2: 3}.get(aid, 1)
                    algo = algo_class(bits=bits)
                else:
                    algo = algo_class()

                header_bytes = algo.extract(frames_array, HEADER_SIZE)
                parsed = parse_header(header_bytes)

                if parsed:
                    log_emitter.emit(f"Header Found in {name}")
                    crc_ok = parsed.get("crc", 0) != 0
                    if crc_ok:
                        log_emitter.emit("CRC32 Verified")
                    else:
                        log_emitter.emit("CRC32 verification skipped")
                    detected_algo_id = aid
                    header_info = parsed
                    log_emitter.emit(f"Algorithm Detected: {name}")

                    self.progress.emit(60)
                    log_emitter.emit("Extracting audio...")
                    payload_size = parsed["payload_size"]
                    total_to_extract = HEADER_SIZE + payload_size
                    payload_raw = algo.extract(frames_array, total_to_extract)
                    payload = payload_raw[HEADER_SIZE:HEADER_SIZE + payload_size]
                    break
                else:
                    log_emitter.emit("Failed")

            if detected_algo_id is None or payload is None:
                raise ValueError("Could not detect algorithm or extract payload")

            self.progress.emit(80)
            log_emitter.emit(f"Saving extracted audio ({len(payload)} bytes)...")
            with open(self.output_path, "wb") as f:
                f.write(payload)

            self.progress.emit(100)
            log_emitter.emit("Extraction completed successfully!")
            self.finished.emit(
                self.output_path,
                {
                    "algorithm_id": detected_algo_id,
                    "algorithm_name": ALGORITHM_NAMES.get(detected_algo_id, "Unknown"),
                    "payload_size": header_info["payload_size"],
                    "audio_format": header_info["audio_format"],
                    "version": header_info["version"],
                },
            )

        except Exception as e:
            log_emitter.emit(f"Extraction failed: {str(e)}")
            self.error.emit(str(e))
