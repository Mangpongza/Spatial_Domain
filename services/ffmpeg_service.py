import subprocess
import os
import shutil
from utils.logging import log_emitter


class FFmpegService:
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()

    @staticmethod
    def _find_ffmpeg() -> str:
        return shutil.which("ffmpeg") or "ffmpeg"

    def extract_audio(self, video_path: str, output_path: str) -> bool:
        log_emitter.emit(f"Extracting audio from video...")
        cmd = [
            self.ffmpeg_path, "-i", video_path,
            "-vn", "-acodec", "copy",
            "-y", output_path
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300
            )
            if result.returncode != 0:
                log_emitter.emit(f"FFmpeg audio extraction warning: {result.stderr[:200]}")
            return os.path.exists(output_path)
        except Exception as e:
            log_emitter.emit(f"FFmpeg error: {str(e)}")
            return False

    def combine_audio_video(
        self, video_frames_path: str, original_audio: str,
        output_path: str, fps: float
    ) -> bool:
        log_emitter.emit(f"Recombining video with audio...")
        temp_video = video_frames_path.replace(".mp4", "_novideo.mp4")
        cmd_build = [
            self.ffmpeg_path, "-framerate", str(fps),
            "-i", video_frames_path,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-y", temp_video
        ]
        try:
            subprocess.run(cmd_build, capture_output=True, text=True, timeout=600)
        except Exception as e:
            log_emitter.emit(f"FFmpeg video build error: {str(e)}")
            return False

        if os.path.exists(original_audio):
            cmd_combine = [
                self.ffmpeg_path, "-i", temp_video,
                "-i", original_audio,
                "-c:v", "copy", "-c:a", "copy",
                "-map", "0:v:0", "-map", "1:a:0",
                "-shortest", "-y", output_path
            ]
            try:
                subprocess.run(cmd_combine, capture_output=True, text=True, timeout=600)
            except Exception as e:
                log_emitter.emit(f"FFmpeg combine error: {str(e)}")
                shutil.move(temp_video, output_path)
        else:
            shutil.move(temp_video, output_path)
        return os.path.exists(output_path)

    def frames_to_video(
        self, frames_pattern: str, output_path: str,
        fps: float, original_audio: str = ""
    ) -> bool:
        return self.combine_audio_video(frames_pattern, original_audio, output_path, fps)

    @staticmethod
    def is_available() -> bool:
        return shutil.which("ffmpeg") is not None
