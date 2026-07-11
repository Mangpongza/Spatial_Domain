import os
from models.audio_model import AudioModel
from utils.logging import log_emitter


class AudioService:
    def __init__(self):
        self.model = AudioModel()

    def open(self, path: str) -> AudioModel:
        log_emitter.emit(f"Opening audio: {os.path.basename(path)}")
        if not self.model.load(path):
            raise ValueError(f"Failed to open audio: {path}")
        return self.model

    def get_bytes(self, model: AudioModel) -> bytes:
        return model.get_raw_bytes()

    def save_bytes(self, data: bytes, output_path: str):
        log_emitter.emit(f"Saving audio to: {os.path.basename(output_path)}")
        with open(output_path, "wb") as f:
            f.write(data)
        log_emitter.emit("Audio saved successfully")
