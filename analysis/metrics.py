import time
import numpy as np
from skimage.metrics import structural_similarity as ssim
from algorithms import get_algorithm
from utils.header import HEADER_SIZE


class MetricsAnalyzer:
    def __init__(self):
        self.metrics: dict = {}

    def analyze_embedding(
        self,
        original_frames: np.ndarray,
        stego_frames: np.ndarray,
        payload: bytes,
        algorithm_id: int,
        embed_time: float,
        extract_time: float,
    ) -> dict:
        algo_class = get_algorithm(algorithm_id)
        if algorithm_id in (0, 1, 2):
            bits = {0: 1, 1: 2, 2: 3}.get(algorithm_id, 1)
            algo = algo_class(bits=bits)
        else:
            algo = algo_class()

        diff = original_frames.astype(np.int16) - stego_frames.astype(np.int16)
        mse = float(np.mean(diff ** 2))
        psnr = float('inf') if mse == 0 else float(20 * np.log10(255.0 / np.sqrt(mse)))

        data_range = 255
        orig_gray = np.mean(original_frames.astype(np.float32), axis=3)
        stego_gray = np.mean(stego_frames.astype(np.float32), axis=3)
        ssim_val = float(ssim(
            orig_gray,
            stego_gray,
            data_range=data_range,
            win_size=3,
            channel_axis=None,
        ))

        payload_capacity = algo.capacity(original_frames)
        total_payload_size = len(payload) + HEADER_SIZE
        payload_usage = (total_payload_size / payload_capacity * 100) if payload_capacity > 0 else 0

        payload_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
        extracted = algo.extract(stego_frames, len(payload) + HEADER_SIZE)
        extracted_payload = extracted[HEADER_SIZE:HEADER_SIZE + len(payload)]
        extracted_bits = np.unpackbits(np.frombuffer(extracted_payload, dtype=np.uint8))[:len(payload_bits)]
        if len(extracted_bits) > 0:
            ber = float(np.sum(payload_bits[:len(extracted_bits)] != extracted_bits) / len(extracted_bits))
        else:
            ber = 0.0

        self.metrics = {
            "psnr": psnr,
            "ssim": ssim_val,
            "mse": mse,
            "embedding_time": embed_time,
            "extraction_time": extract_time,
            "payload_capacity": payload_capacity,
            "payload_usage": payload_usage,
            "ber": ber,
            "payload_size": len(payload),
            "compression_ratio": payload_capacity / len(payload) if len(payload) > 0 else 0,
        }
        return self.metrics

    def histogram_comparison(self, original: np.ndarray, modified: np.ndarray) -> dict:
        result = {}
        for c, name in enumerate(["R", "G", "B"]):
            orig_hist = np.histogram(original[:, :, :, c].ravel(), bins=256, range=(0, 255))[0]
            mod_hist = np.histogram(modified[:, :, :, c].ravel(), bins=256, range=(0, 255))[0]
            diff_hist = np.sum(np.abs(orig_hist.astype(np.int32) - mod_hist.astype(np.int32)))
            result[name] = {
                "original": orig_hist.tolist(),
                "modified": mod_hist.tolist(),
                "difference": int(diff_hist),
            }
        return result

    def frame_difference(self, original: np.ndarray, modified: np.ndarray) -> np.ndarray:
        return np.mean((original.astype(np.float32) - modified.astype(np.float32)) ** 2, axis=3)

    def noise_map(self, original: np.ndarray, modified: np.ndarray) -> np.ndarray:
        return np.abs(original.astype(np.int16) - modified.astype(np.int16)).astype(np.uint8)

    def frame_capacity(self, frames: np.ndarray, algorithm_id: int) -> int:
        algo_class = get_algorithm(algorithm_id)
        if algorithm_id in (0, 1, 2):
            bits = {0: 1, 1: 2, 2: 3}.get(algorithm_id, 1)
            algo = algo_class(bits=bits)
        else:
            algo = algo_class()
        return algo.capacity(frames)
