import os
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
            ffmpeg = FFmpegService()

            video_model = video_service.open(self.video_path)
            audio_model = audio_service.open(self.audio_path)

            self.progress.emit(10)
            log_emitter.emit("Extracting original audio from video...")
            temp_audio = os.path.join(
                os.path.dirname(self.output_path), "_original_audio.wav"
            )
            ffmpeg.extract_audio(self.video_path, temp_audio)
            video_model.original_audio_path = temp_audio

            self.progress.emit(20)
            frames_array = video_service.read_all_frames(video_model)

            self.progress.emit(30)
            log_emitter.emit("Converting audio to binary...")
            audio_data = audio_service.get_bytes(audio_model)
            payload = audio_data
            payload_size = len(payload)

            self.progress.emit(40)
            log_emitter.emit("Building header...")
            header = build_header(
                algorithm_id=self.algorithm_id,
                lsb_mode=self.lsb_mode,
                payload_size=payload_size,
                audio_format=audio_model.model.format_id,
                version=1,
            )

            full_payload = header + payload

            self.progress.emit(50)
            log_emitter.emit("Checking capacity...")
            algo_class = get_algorithm(self.algorithm_id)
            algo = algo_class()
            if self.algorithm_id in (0, 1, 2):
                bits = {0: 1, 1: 2, 2: 3}.get(self.algorithm_id, 1)
                algo = algo_class(bits=bits)
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
            video_service.frames_to_video(
                stego_frames, self.output_path, video_model.fps
            )

            self.progress.emit(90)
            if os.path.exists(temp_audio):
                log_emitter.emit("Re-adding audio track...")
                temp_novideo = self.output_path.replace(".mp4", "_novideo.mp4")
                os.rename(self.output_path, temp_novideo)
                ffmpeg.combine_audio_video(
                    temp_novideo, temp_audio, self.output_path, video_model.fps
                )
                if os.path.exists(temp_novideo):
                    os.remove(temp_novideo)

            self.progress.emit(100)
            log_emitter.emit("Embedding completed successfully!")
            self.finished.emit(self.output_path)

        except Exception as e:
            log_emitter.emit(f"Embedding failed: {str(e)}")
            self.error.emit(str(e))
