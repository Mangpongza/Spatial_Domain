import numpy as np
from algorithms import BaseStegoAlgorithm


class AdaptiveLSB(BaseStegoAlgorithm):
    algorithm_id = 4
    algorithm_name = "Adaptive LSB"

    def __init__(self, bits: int = 1):
        self.bits = bits

    def embed(self, frames: np.ndarray, payload: bytes) -> np.ndarray:
        data_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
        stego = frames.copy()
        gray = np.mean(frames.astype(np.float32), axis=3).astype(np.uint8)
        flat_gray = gray.ravel()
        flat_stego = stego[:, :, :, 0].ravel()
        bit_idx = 0
        for i in range(len(flat_gray)):
            if bit_idx >= len(data_bits):
                break
            local_complexity = self._compute_complexity(flat_gray, i, len(flat_gray))
            k = min(self.bits + int(local_complexity * 2), 3)
            if k < 1:
                k = 1
            c_mask = (1 << k) - 1
            bits_to_take = min(k, len(data_bits) - bit_idx)
            if bits_to_take <= 0:
                break
            val = 0
            for b in range(bits_to_take):
                val |= int(data_bits[bit_idx + b]) << b
            pval = int(flat_stego[i])
            pval = (pval & ~c_mask) | (val & c_mask)
            flat_stego[i] = np.clip(pval, 0, 255)
            bit_idx += bits_to_take
        stego[:, :, :, 0] = flat_stego.reshape(stego[:, :, :, 0].shape)
        return stego

    def _compute_complexity(self, arr: np.ndarray, idx: int, length: int):
        if idx < 4 or idx >= length - 4:
            return 0.0
        neighborhood = arr[idx - 4:idx + 5]
        return float(np.std(neighborhood)) / 128.0

    def extract(self, frames: np.ndarray, payload_size: int) -> bytes:
        gray = np.mean(frames.astype(np.float32), axis=3).astype(np.uint8)
        flat_gray = gray.ravel()
        flat_r = frames[:, :, :, 0].ravel()
        total_bits = payload_size * 8
        bits = []
        i = 0
        n_pixels = len(flat_gray)
        while len(bits) < total_bits and i < n_pixels:
            local_complexity = self._compute_complexity(flat_gray, i, n_pixels)
            k = min(self.bits + int(local_complexity * 2), 3)
            if k < 1:
                k = 1
            c_mask = (1 << k) - 1
            val = int(flat_r[i]) & c_mask
            for b in range(k):
                bits.append((val >> b) & 1)
            i += 1
        bits_arr = np.array(bits[:total_bits], dtype=np.uint8)
        return np.packbits(bits_arr).tobytes()[:payload_size]

    def capacity(self, frames: np.ndarray) -> int:
        return int(frames.shape[0]) * int(frames.shape[1]) * int(frames.shape[2]) * self.bits // 8

    def analyze(self, original: np.ndarray, modified: np.ndarray) -> dict:
        diff = original.astype(np.int16) - modified.astype(np.int16)
        mse = float(np.mean(diff ** 2))
        psnr = float('inf') if mse == 0 else float(20 * np.log10(255.0 / np.sqrt(mse)))
        return {"mse": mse, "psnr": psnr}
