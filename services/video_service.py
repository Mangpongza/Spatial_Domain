import os
import cv2
import numpy as np
from models.video_model import VideoModel
from utils.logging import log_emitter


class VideoService:
    def __init__(self):
        self.model = VideoModel()

    def open(self, path: str) -> VideoModel:
        log_emitter.emit(f"Opening video: {os.path.basename(path)}")
        if not self.model.load(path):
            raise ValueError(f"Failed to open video: {path}")
        return self.model

    def read_all_frames(self, model: VideoModel) -> np.ndarray:
        log_emitter.emit("Reading frames...")
        frames = model.read_frames()
        log_emitter.emit(f"Loaded {len(frames)} frames")
        return np.array(frames)

    def write_frames_to_images(
        self, frames: np.ndarray, output_dir: str, prefix: str = "frame"
    ) -> str:
        os.makedirs(output_dir, exist_ok=True)
        log_emitter.emit(f"Writing {len(frames)} frames to {output_dir}")
        for i, frame in enumerate(frames):
            cv2.imwrite(
                os.path.join(output_dir, f"{prefix}_{i:06d}.png"), frame
            )
        return os.path.join(output_dir, f"{prefix}_%06d.png")

    def frames_to_video(
        self, frames: np.ndarray, output_path: str, fps: float
    ):
        log_emitter.emit(f"Rebuilding video: {output_path}")
        h, w = frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        for frame in frames:
            out.write(frame)
        out.release()
        log_emitter.emit("Video rebuilt successfully")
