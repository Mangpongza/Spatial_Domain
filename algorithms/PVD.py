import numpy as np
from algorithms import BaseStegoAlgorithm


class PVD(BaseStegoAlgorithm):
    algorithm_id = 8
    algorithm_name = "PVD"

    def __init__(self, bits: int = 2):
        self.bits = bits

    RANGES = [
        (0, 15, 4),
        (16, 63, 16),
        (64, 127, 64),
        (128, 255, 128),
    ]

    def _get_range(self, diff: int) -> tuple:
        for l, u, step in self.RANGES:
            if l <= diff <= u:
                return (l, u, step)
        return self.RANGES[-1]

    def embed(self, frames: np.ndarray, payload: bytes) -> np.ndarray:
        data_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
        stego = frames.copy()
        flat = stego[:, :, :, 0].ravel()
        bit_idx = 0
        n = len(flat)
        for i in range(0, n - 1, 2):
            if bit_idx >= len(data_bits):
                break
            p1 = int(flat[i])
            p2 = int(flat[i + 1])
            diff = abs(p2 - p1)
            l, u, step = self._get_range(diff)
            k = int(np.log2(step))
            bits_to_take = min(k, len(data_bits) - bit_idx)
            if bits_to_take <= 0:
                continue
            bits_val = 0
            for b in range(bits_to_take):
                bits_val |= int(data_bits[bit_idx + b]) << b
            d_new = l + bits_val
            p1_new = max(0, p1)
            p2_new = p1_new + d_new
            if p2_new > 255:
                p2_new = 255
                p1_new = p2_new - d_new
                if p1_new < 0:
                    p1_new = 0
                    p2_new = d_new
            flat[i] = int(p1_new)
            flat[i + 1] = int(p2_new)
            bit_idx += bits_to_take
        stego[:, :, :, 0] = flat.reshape(stego[:, :, :, 0].shape)
        return stego

    def extract(self, frames: np.ndarray, payload_size: int) -> bytes:
        flat = frames[:, :, :, 0].ravel()
        total_bits = payload_size * 8
        bits = []
        n = len(flat)
        for i in range(0, n - 1, 2):
            if len(bits) >= total_bits:
                break
            diff = abs(int(flat[i + 1]) - int(flat[i]))
            l, u, step = self._get_range(diff)
            k = int(np.log2(step))
            bits_val = diff - l
            for b in range(k):
                bits.append((bits_val >> b) & 1)
        bits_arr = np.array(bits[:total_bits], dtype=np.uint8)
        return np.packbits(bits_arr).tobytes()[:payload_size]

    def capacity(self, frames: np.ndarray) -> int:
        flat = frames[:, :, :, 0].ravel()
        total_bits = 0
        n = len(flat)
        for i in range(0, n - 1, 2):
            diff = abs(int(flat[i + 1]) - int(flat[i]))
            l, u, step = self._get_range(diff)
            k = int(np.log2(step))
            total_bits += k
        return total_bits // 8

    def analyze(self, original: np.ndarray, modified: np.ndarray) -> dict:
        diff = original.astype(np.int16) - modified.astype(np.int16)
        mse = float(np.mean(diff ** 2))
        psnr = float('inf') if mse == 0 else float(20 * np.log10(255.0 / np.sqrt(mse)))
        return {"mse": mse, "psnr": psnr}
