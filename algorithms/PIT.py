import numpy as np
from algorithms import BaseStegoAlgorithm


class PIT(BaseStegoAlgorithm):
    algorithm_id = 11
    algorithm_name = "PIT"

    def __init__(self, bits: int = 1):
        self.bits = bits

    def embed(self, frames: np.ndarray, payload: bytes) -> np.ndarray:
        data_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
        stego = frames.copy()
        flat = stego[:, :, :, 0].ravel()
        bit_idx = 0
        n = len(flat)
        for i in range(0, n - 2, 3):
            if bit_idx >= len(data_bits):
                break
            trio = [int(flat[i]), int(flat[i + 1]), int(flat[i + 2])]
            sorted_vals = sorted([(trio[0], 0), (trio[1], 1), (trio[2], 2)])
            bit_val = int(data_bits[bit_idx])
            parity = (sorted_vals[0][0] % 2) ^ (sorted_vals[1][0] % 2) ^ (sorted_vals[2][0] % 2)
            if parity != bit_val:
                idx_to_modify = sorted_vals[1][1]
                if trio[idx_to_modify] < 255:
                    trio[idx_to_modify] += 1
                else:
                    trio[idx_to_modify] -= 1
            flat[i] = np.clip(trio[0], 0, 255)
            flat[i + 1] = np.clip(trio[1], 0, 255)
            flat[i + 2] = np.clip(trio[2], 0, 255)
            bit_idx += 1
        stego[:, :, :, 0] = flat.reshape(stego[:, :, :, 0].shape)
        return stego

    def extract(self, frames: np.ndarray, payload_size: int) -> bytes:
        flat = frames[:, :, :, 0].ravel()
        total_bits = payload_size * 8
        bits = []
        n = len(flat)
        for i in range(0, n - 2, 3):
            if len(bits) >= total_bits:
                break
            trio = [int(flat[i]), int(flat[i + 1]), int(flat[i + 2])]
            sorted_vals = sorted([(trio[0], 0), (trio[1], 1), (trio[2], 2)])
            parity = (sorted_vals[0][0] % 2) ^ (sorted_vals[1][0] % 2) ^ (sorted_vals[2][0] % 2)
            bits.append(parity)
        bits_arr = np.array(bits[:total_bits], dtype=np.uint8)
        return np.packbits(bits_arr).tobytes()[:payload_size]

    def capacity(self, frames: np.ndarray) -> int:
        return int(frames.shape[0]) * int(frames.shape[1]) * int(frames.shape[2]) // 24

    def analyze(self, original: np.ndarray, modified: np.ndarray) -> dict:
        diff = original.astype(np.int16) - modified.astype(np.int16)
        mse = float(np.mean(diff ** 2))
        psnr = float('inf') if mse == 0 else float(20 * np.log10(255.0 / np.sqrt(mse)))
        return {"mse": mse, "psnr": psnr}
