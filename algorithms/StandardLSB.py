import numpy as np
from algorithms import BaseStegoAlgorithm


class StandardLSB(BaseStegoAlgorithm):
    algorithm_id = 0
    algorithm_name = "Standard LSB"

    def __init__(self, bits: int = 1):
        self.bits = bits
        if bits == 1:
            self.algorithm_id = 0
        elif bits == 2:
            self.algorithm_id = 1
        elif bits == 3:
            self.algorithm_id = 2

    def embed(self, frames: np.ndarray, payload: bytes) -> np.ndarray:
        data_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
        stego = frames.copy()
        flat = stego[:, :, :, 0].ravel()
        mask = (1 << self.bits) - 1
        for i in range(min(len(data_bits), len(flat))):
            pval = int(flat[i])
            pval = (pval & ~mask) | (int(data_bits[i]) & mask)
            flat[i] = np.clip(pval, 0, 255)
        stego[:, :, :, 0] = flat.reshape(stego[:, :, :, 0].shape)
        return stego

    def extract(self, frames: np.ndarray, payload_size: int) -> bytes:
        flat = frames[:, :, :, 0].ravel()
        total_bits = payload_size * 8
        n_pixels = len(flat)
        mask = (1 << self.bits) - 1
        limit = min(total_bits, n_pixels)
        bits = np.array([int(flat[i]) & mask for i in range(limit)], dtype=np.uint8)
        return np.packbits(bits).tobytes()[:payload_size]

    def capacity(self, frames: np.ndarray) -> int:
        return int(frames.shape[0]) * int(frames.shape[1]) * int(frames.shape[2]) * self.bits // 8

    def analyze(self, original: np.ndarray, modified: np.ndarray) -> dict:
        diff = original.astype(np.int16) - modified.astype(np.int16)
        mse = float(np.mean(diff ** 2))
        psnr = float('inf') if mse == 0 else float(20 * np.log10(255.0 / np.sqrt(mse)))
        return {"mse": mse, "psnr": psnr}
