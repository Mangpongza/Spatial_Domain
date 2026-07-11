import numpy as np
from scipy import ndimage
from algorithms import BaseStegoAlgorithm


class EdgeBasedLSB(BaseStegoAlgorithm):
    algorithm_id = 5
    algorithm_name = "Edge-based LSB"

    def __init__(self, bits: int = 1):
        self.bits = bits

    def _get_edge_mask(self, frames: np.ndarray) -> np.ndarray:
        gray = frames[:, :, :, 1].astype(np.float32)
        sobel_x = ndimage.sobel(gray, axis=2)
        sobel_y = ndimage.sobel(gray, axis=1)
        magnitude = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
        threshold = np.percentile(magnitude, 75)
        return magnitude >= threshold

    def embed(self, frames: np.ndarray, payload: bytes) -> np.ndarray:
        data_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
        stego = frames.copy()
        edge_mask = self._get_edge_mask(frames)
        flat_r = stego[:, :, :, 0].ravel()
        flat_edge = edge_mask.ravel()
        bit_idx = 0
        for i in range(len(flat_r)):
            if bit_idx >= len(data_bits):
                break
            k = self.bits
            c_mask = (1 << k) - 1
            pval = int(flat_r[i])
            pval = (pval & ~c_mask) | (int(data_bits[bit_idx]) & c_mask)
            flat_r[i] = np.clip(pval, 0, 255)
            bit_idx += 1
        stego[:, :, :, 0] = flat_r.reshape(stego[:, :, :, 0].shape)
        return stego

    def extract(self, frames: np.ndarray, payload_size: int) -> bytes:
        flat_r = frames[:, :, :, 0].ravel()
        total_bits = payload_size * 8
        n_pixels = len(flat_r)
        limit = min(total_bits, n_pixels)
        mask = (1 << self.bits) - 1
        bits = np.array([int(flat_r[i]) & mask for i in range(limit)], dtype=np.uint8)
        return np.packbits(bits).tobytes()[:payload_size]

    def capacity(self, frames: np.ndarray) -> int:
        return int(frames.shape[0]) * int(frames.shape[1]) * int(frames.shape[2]) * self.bits // 8

    def analyze(self, original: np.ndarray, modified: np.ndarray) -> dict:
        diff = original.astype(np.int16) - modified.astype(np.int16)
        mse = float(np.mean(diff ** 2))
        psnr = float('inf') if mse == 0 else float(20 * np.log10(255.0 / np.sqrt(mse)))
        return {"mse": mse, "psnr": psnr}
