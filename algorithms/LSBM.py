import numpy as np
from algorithms import BaseStegoAlgorithm


class LSBM(BaseStegoAlgorithm):
    algorithm_id = 6
    algorithm_name = "LSBM"

    def embed(self, frames: np.ndarray, payload: bytes) -> np.ndarray:
        data_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
        stego = frames.copy()
        flat = stego[:, :, :, 0].ravel()
        for i in range(min(len(data_bits), len(flat))):
            bit = int(data_bits[i])
            pval = int(flat[i])
            if bit == 1:
                if pval % 2 == 0:
                    pval = pval + 1 if pval < 255 else pval - 1
            else:
                if pval % 2 == 1:
                    pval = pval + 1 if pval < 255 else pval - 1
            flat[i] = np.clip(pval, 0, 255)
        stego[:, :, :, 0] = flat.reshape(stego[:, :, :, 0].shape)
        return stego

    def extract(self, frames: np.ndarray, payload_size: int) -> bytes:
        flat = frames[:, :, :, 0].ravel()
        total_bits = payload_size * 8
        n_pixels = len(flat)
        limit = min(total_bits, n_pixels)
        bits = np.array([int(flat[i]) % 2 for i in range(limit)], dtype=np.uint8)
        return np.packbits(bits).tobytes()[:payload_size]

    def capacity(self, frames: np.ndarray) -> int:
        return int(frames.shape[0]) * int(frames.shape[1]) * int(frames.shape[2]) // 8

    def analyze(self, original: np.ndarray, modified: np.ndarray) -> dict:
        diff = original.astype(np.int16) - modified.astype(np.int16)
        mse = float(np.mean(diff ** 2))
        psnr = float('inf') if mse == 0 else float(20 * np.log10(255.0 / np.sqrt(mse)))
        return {"mse": mse, "psnr": psnr}
