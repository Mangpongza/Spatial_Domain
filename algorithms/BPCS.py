import numpy as np
from algorithms import BaseStegoAlgorithm


class BPCS(BaseStegoAlgorithm):
    algorithm_id = 9
    algorithm_name = "BPCS"

    def __init__(self, block_size: int = 8, threshold: int = 60):
        self.block_size = block_size
        self.threshold = threshold

    def _complexity(self, block: np.ndarray) -> float:
        b = (block > block.mean()).astype(np.int32)
        h_changes = float(np.sum(np.abs(np.diff(b, axis=1))))
        v_changes = float(np.sum(np.abs(np.diff(b, axis=0))))
        max_changes = (b.shape[0] * (b.shape[1] - 1)) + ((b.shape[0] - 1) * b.shape[1])
        return (h_changes + v_changes) / max_changes if max_changes > 0 else 0.0

    def embed(self, frames: np.ndarray, payload: bytes) -> np.ndarray:
        data_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
        stego = frames.copy()
        bit_idx = 0
        for f in range(frames.shape[0]):
            if bit_idx >= len(data_bits):
                break
            channel = stego[f, :, :, 0]
            h, w = channel.shape
            for y in range(0, h - self.block_size + 1, self.block_size):
                for x in range(0, w - self.block_size + 1, self.block_size):
                    if bit_idx >= len(data_bits):
                        break
                    block = channel[y:y + self.block_size, x:x + self.block_size].copy()
                    n_bits = min(8, len(data_bits) - bit_idx)
                    for bp in range(n_bits):
                        lsb = (block.ravel()[bp] & 1)
                        if lsb != data_bits[bit_idx + bp]:
                            new_val = block.ravel()[bp] ^ 1
                            block.ravel()[bp] = new_val
                    bit_idx += n_bits
                    channel[y:y + self.block_size, x:x + self.block_size] = block
            stego[f, :, :, 0] = channel
        return stego

    def extract(self, frames: np.ndarray, payload_size: int) -> bytes:
        total_bits = payload_size * 8
        bits = []
        for f in range(frames.shape[0]):
            if len(bits) >= total_bits:
                break
            channel = frames[f, :, :, 0]
            h, w = channel.shape
            for y in range(0, h - self.block_size + 1, self.block_size):
                for x in range(0, w - self.block_size + 1, self.block_size):
                    if len(bits) >= total_bits:
                        break
                    block = channel[y:y + self.block_size, x:x + self.block_size]
                    n_bits = min(8, total_bits - len(bits))
                    for bp in range(n_bits):
                        bits.append(int(block.ravel()[bp]) & 1)
        bits_arr = np.array(bits[:total_bits], dtype=np.uint8)
        return np.packbits(bits_arr).tobytes()[:payload_size]

    def capacity(self, frames: np.ndarray) -> int:
        n_frames = int(frames.shape[0])
        h = int(frames.shape[1])
        w = int(frames.shape[2])
        n_blocks = (h // self.block_size) * (w // self.block_size)
        return n_blocks * 8 * n_frames // 8

    def analyze(self, original: np.ndarray, modified: np.ndarray) -> dict:
        diff = original.astype(np.int16) - modified.astype(np.int16)
        mse = float(np.mean(diff ** 2))
        psnr = float('inf') if mse == 0 else float(20 * np.log10(255.0 / np.sqrt(mse)))
        return {"mse": mse, "psnr": psnr}
