import os
import math
import time
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from models.video_model import VideoModel
from models.audio_model import AudioModel
from services.video_service import VideoService
from services.audio_service import AudioService
from services.ffmpeg_service import FFmpegService
from algorithms import get_algorithm
from utils.header import build_header, HEADER_SIZE
from utils.logging import log_emitter


class EmbedWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(
        self,
        video_path: str,
        audio_path: str,
        output_path: str,
        algorithm_id: int,
        lsb_mode: int = 1,
    ):
        super().__init__()
        self.video_path = video_path
        self.audio_path = audio_path
        self.output_path = output_path
        self.algorithm_id = algorithm_id
        self.lsb_mode = lsb_mode

    def run(self):
        try:
            self.progress.emit(5)
            log_emitter.emit("Starting embedding process...")

            video_service = VideoService()
            audio_service = AudioService()

            video_model = video_service.open(self.video_path)
            audio_model = audio_service.open(self.audio_path)

            self.progress.emit(20)
            log_emitter.emit("Converting audio to bytes...")
            audio_data = audio_service.get_bytes(audio_model)
            payload = audio_data
            payload_size = len(payload)

            self.progress.emit(30)
            log_emitter.emit("Building header...")
            header = build_header(
                algorithm_id=self.algorithm_id,
                lsb_mode=self.lsb_mode,
                payload_size=payload_size,
                audio_format=audio_model.format_id,
                version=1,
            )

            full_payload = header + payload

            # Calculate how many frames we need
            bits_per_px = self.lsb_mode
            if self.algorithm_id in (0, 1, 2):
                bits_per_px = {0: 1, 1: 2, 2: 3}.get(self.algorithm_id, 1)
            bits_per_frame = video_model.width * video_model.height * bits_per_px
            needed_frames = math.ceil(len(full_payload) * 8 / bits_per_frame)

            log_emitter.emit(f"Need {needed_frames} frames (capacity: {bits_per_frame} bits/frame)")

            # Cap to available frames (but log warning if not enough)
            if needed_frames > video_model.total_frames:
                raise ValueError(
                    f"Audio too large! Need {needed_frames} frames but video only has {video_model.total_frames}. "
                    f"Use shorter audio, higher resolution video, or more bits per pixel."
                )

            self.progress.emit(40)
            log_emitter.emit(f"Reading all {video_model.total_frames} frames...")
            frames_array = video_service.read_all_frames(video_model)
            actual_frames = len(frames_array)
            log_emitter.emit(f"Read {actual_frames} frames")

            # Check capacity with actual frames
            algo_class = get_algorithm(self.algorithm_id)
            if self.algorithm_id in (0, 1, 2):
                bits = bits_per_px
                algo = algo_class(bits=bits)
            else:
                algo = algo_class()
            cap = algo.capacity(frames_array)
            if len(full_payload) > cap:
                raise ValueError(
                    f"Payload too large! Need {len(full_payload)} bytes, max {cap} bytes"
                )

            self.progress.emit(60)
            log_emitter.emit(f"Embedding using {algo.algorithm_name}...")
            embed_start = time.time()
            stego_frames = algo.embed(frames_array, full_payload)
            embed_time = time.time() - embed_start
            log_emitter.emit(f"Embedding completed in {embed_time:.2f}s")

            self.progress.emit(80)
            log_emitter.emit("Rebuilding video...")
            actual_output = video_service.frames_to_video(
                stego_frames, self.output_path, video_model.fps,
                original_codec=video_model.codec
            )
            if actual_output:
                self.output_path = actual_output

            self.progress.emit(100)
            log_emitter.emit(f"Embedding completed successfully! Saved to: {self.output_path}")
            self.finished.emit(self.output_path)

        except Exception as e:
            log_emitter.emit(f"Embedding failed: {str(e)}")
            self.error.emit(str(e))
