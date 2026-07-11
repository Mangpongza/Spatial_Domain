import numpy as np
from algorithms import BaseStegoAlgorithm


class OPAP(BaseStegoAlgorithm):
    algorithm_id = 10
    algorithm_name = "OPAP"

    def __init__(self, bits: int = 1):
        self.bits = bits

    def embed(self, frames: np.ndarray, payload: bytes) -> np.ndarray:
        data_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
        stego = frames.copy()
        flat = stego[:, :, :, 0].ravel()
        for i in range(min(len(data_bits), len(flat))):
            s = int(data_bits[i])
            pval = int(flat[i])
            pi = pval & 1
            if pi != s:
                diff = s - pi
                candidate1 = pval + diff
                candidate2 = pval + diff - 2 if diff > 0 else pval + diff + 2
                err1 = abs(pval - candidate1)
                err2 = abs(pval - candidate2)
                best = candidate1 if err1 <= err2 else candidate2
                pval = int(np.clip(best, 0, 255))
            pval = (pval & 0xFE) | s
            flat[i] = np.clip(pval, 0, 255)
        stego[:, :, :, 0] = flat.reshape(stego[:, :, :, 0].shape)
        return stego

    def extract(self, frames: np.ndarray, payload_size: int) -> bytes:
        flat = frames[:, :, :, 0].ravel()
        total_bits = payload_size * 8
        n_pixels = len(flat)
        limit = min(total_bits, n_pixels)
        bits = np.array([int(flat[i]) & 1 for i in range(limit)], dtype=np.uint8)
        return np.packbits(bits).tobytes()[:payload_size]

    def capacity(self, frames: np.ndarray) -> int:
        return int(frames.shape[0]) * int(frames.shape[1]) * int(frames.shape[2]) // 8

    def analyze(self, original: np.ndarray, modified: np.ndarray) -> dict:
        diff = original.astype(np.int16) - modified.astype(np.int16)
        mse = float(np.mean(diff ** 2))
        psnr = float('inf') if mse == 0 else float(20 * np.log10(255.0 / np.sqrt(mse)))
        return {"mse": mse, "psnr": psnr}
