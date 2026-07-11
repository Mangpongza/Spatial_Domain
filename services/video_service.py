import os
import cv2
import numpy as np
from models.video_model import VideoModel
from utils.logging import log_emitter

LOSSLESS_CODECS = [("FFV1", ".mkv"), ("HFYU", ".avi"), ("PNG ", ".avi")]


class VideoService:
    def __init__(self):
        self.model = VideoModel()

    def open(self, path: str) -> VideoModel:
        log_emitter.emit(f"Opening video: {os.path.basename(path)}")
        if not self.model.load(path):
            raise ValueError(f"Failed to open video: {path}")
        return self.model

    def read_all_frames(self, model: VideoModel, max_frames: int = 0) -> np.ndarray:
        log_emitter.emit("Reading frames...")
        frames = model.read_frames(max_frames)
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
    ) -> str:
        log_emitter.emit(f"Rebuilding video: {output_path}")
        h, w = frames[0].shape[:2]
        base = os.path.splitext(output_path)[0]

        for codec, ext in LOSSLESS_CODECS:
            lossless_path = f"{base}{ext}"
            fourcc = cv2.VideoWriter_fourcc(*codec)
            out = cv2.VideoWriter(lossless_path, fourcc, fps, (w, h))
            if out.isOpened():
                for frame in frames:
                    out.write(frame)
                out.release()
                if os.path.exists(lossless_path) and os.path.getsize(lossless_path) > 0:
                    log_emitter.emit(f"Saved lossless video: {lossless_path}")
                    return lossless_path
            out.release()

        log_emitter.emit("WARNING: No lossless codec available, falling back to mp4v")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        if out.isOpened():
            for frame in frames:
                out.write(frame)
            out.release()
            log_emitter.emit("Video rebuilt successfully")
            return output_path
        out.release()
        raise RuntimeError("Could not open any VideoWriter codec")
