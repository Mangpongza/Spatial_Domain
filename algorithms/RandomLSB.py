import numpy as np
import random
from algorithms import BaseStegoAlgorithm


class RandomLSB(BaseStegoAlgorithm):
    algorithm_id = 3
    algorithm_name = "Random LSB"

    def __init__(self, seed: int = 42, bits: int = 1):
        self.seed = seed
        self.bits = bits

    def _get_positions(self, total_pixels: int, total_bits: int):
        rng = random.Random(self.seed)
        k = min(total_bits, total_pixels)
        return rng.sample(range(total_pixels), k)

    def embed(self, frames: np.ndarray, payload: bytes) -> np.ndarray:
        data_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
        stego = frames.copy()
        flat = stego[:, :, :, 0].ravel()
        total_bits = len(data_bits)
        n_pixels = len(flat)
        positions = self._get_positions(n_pixels, min(total_bits, n_pixels))
        mask = (1 << self.bits) - 1
        for idx, pos in enumerate(positions):
            if idx >= len(data_bits):
                break
            pval = int(flat[pos])
            pval = (pval & ~mask) | (int(data_bits[idx]) & mask)
            flat[pos] = np.clip(pval, 0, 255)
        stego[:, :, :, 0] = flat.reshape(stego[:, :, :, 0].shape)
        return stego

    def extract(self, frames: np.ndarray, payload_size: int) -> bytes:
        flat = frames[:, :, :, 0].ravel()
        total_bits = payload_size * 8
        n_pixels = len(flat)
        limit = min(total_bits, n_pixels)
        positions = self._get_positions(n_pixels, limit)
        mask = (1 << self.bits) - 1
        bits = np.array([int(flat[pos]) & mask for pos in positions], dtype=np.uint8)
        return np.packbits(bits).tobytes()[:payload_size]

    def capacity(self, frames: np.ndarray) -> int:
        return int(frames.shape[0]) * int(frames.shape[1]) * int(frames.shape[2]) * self.bits // 8

    def analyze(self, original: np.ndarray, modified: np.ndarray) -> dict:
        diff = original.astype(np.int16) - modified.astype(np.int16)
        mse = float(np.mean(diff ** 2))
        psnr = float('inf') if mse == 0 else float(20 * np.log10(255.0 / np.sqrt(mse)))
        return {"mse": mse, "psnr": psnr}
