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
        n_data = len(data_bits)
        n_data_aligned = n_data + (-n_data % self.bits) if n_data % self.bits else n_data
        if n_data_aligned > n_data:
            data_bits = np.pad(data_bits, (0, n_data_aligned - n_data), 'constant')
        n_pixels = min(n_data_aligned // self.bits, len(flat))
        for i in range(n_pixels):
            val = 0
            for b in data_bits[i * self.bits:(i + 1) * self.bits]:
                val = (val << 1) | int(b)
            pval = int(flat[i])
            pval = (pval & ~mask) | (val & mask)
            flat[i] = np.clip(pval, 0, 255)
        stego[:, :, :, 0] = flat.reshape(stego[:, :, :, 0].shape)
        return stego

    def extract(self, frames: np.ndarray, payload_size: int) -> bytes:
        flat = frames[:, :, :, 0].ravel()
        total_bits = payload_size * 8
        n_pixels = min((total_bits + self.bits - 1) // self.bits, len(flat))
        mask = (1 << self.bits) - 1
        bits = []
        for i in range(n_pixels):
            val = int(flat[i]) & mask
            for b in range(self.bits - 1, -1, -1):
                bits.append((val >> b) & 1)
        result = np.array(bits[:total_bits], dtype=np.uint8)
        return np.packbits(result).tobytes()[:payload_size]

    def capacity(self, frames: np.ndarray) -> int:
        return int(frames.shape[0]) * int(frames.shape[1]) * int(frames.shape[2]) * self.bits // 8

    def analyze(self, original: np.ndarray, modified: np.ndarray) -> dict:
        diff = original.astype(np.int16) - modified.astype(np.int16)
        mse = float(np.mean(diff ** 2))
        psnr = float('inf') if mse == 0 else float(20 * np.log10(255.0 / np.sqrt(mse)))
        return {"mse": mse, "psnr": psnr}
