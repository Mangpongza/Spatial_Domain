import numpy as np
from algorithms import BaseStegoAlgorithm


class LSBMR(BaseStegoAlgorithm):
    algorithm_id = 7
    algorithm_name = "LSBMR"

    def embed(self, frames: np.ndarray, payload: bytes) -> np.ndarray:
        data_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
        stego = frames.copy()
        flat_r = stego[:, :, :, 0].ravel()
        flat_g = stego[:, :, :, 1].ravel()
        bit_idx = 0
        n = len(flat_r)
        i = 0
        while i < n and bit_idx < len(data_bits) - 1:
            m1 = int(data_bits[bit_idx])
            m2 = int(data_bits[bit_idx + 1]) if bit_idx + 1 < len(data_bits) else 0
            x = int(flat_r[i])
            y = int(flat_g[i])
            best_cost = 999
            best_x, best_y = x, y
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    nx = np.clip(x + dx, 0, 255)
                    ny = np.clip(y + dy, 0, 255)
                    if nx % 2 == m1 and ((nx // 2) + ny) % 2 == m2:
                        cost = abs(nx - x) + abs(ny - y)
                        if cost < best_cost:
                            best_cost = cost
                            best_x, best_y = nx, ny
            if best_cost < 999:
                flat_r[i] = best_x
                flat_g[i] = best_y
            bit_idx += 2
            i += 1
        stego[:, :, :, 0] = flat_r.reshape(stego[:, :, :, 0].shape)
        stego[:, :, :, 1] = flat_g.reshape(stego[:, :, :, 1].shape)
        return stego

    def extract(self, frames: np.ndarray, payload_size: int) -> bytes:
        flat_r = frames[:, :, :, 0].ravel()
        flat_g = frames[:, :, :, 1].ravel()
        total_bits = payload_size * 8
        bits = []
        n = len(flat_r)
        for i in range(n):
            if len(bits) >= total_bits:
                break
            x = int(flat_r[i])
            y = int(flat_g[i])
            bits.append(x % 2)
            bits.append(((x // 2) + y) % 2)
        bits_arr = np.array(bits[:total_bits], dtype=np.uint8)
        return np.packbits(bits_arr).tobytes()[:payload_size]

    def capacity(self, frames: np.ndarray) -> int:
        return int(frames.shape[0]) * int(frames.shape[1]) * int(frames.shape[2]) // 4

    def analyze(self, original: np.ndarray, modified: np.ndarray) -> dict:
        diff = original.astype(np.int16) - modified.astype(np.int16)
        mse = float(np.mean(diff ** 2))
        psnr = float('inf') if mse == 0 else float(20 * np.log10(255.0 / np.sqrt(mse)))
        return {"mse": mse, "psnr": psnr}
