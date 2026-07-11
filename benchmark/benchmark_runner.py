import time
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from algorithms import get_algorithm
from utils.constants import ALGORITHM_NAMES
from utils.logging import log_emitter


class BenchmarkRunner(QThread):
    progress = pyqtSignal(int, int)
    result_ready = pyqtSignal(int, dict)
    finished = pyqtSignal(list)

    def __init__(self, frames: np.ndarray, payload_size: int = 1024):
        super().__init__()
        self.frames = frames
        self.payload_size = payload_size
        self.results = []

    def run(self):
        log_emitter.emit("Starting benchmark...")
        algo_ids = [0, 1, 2, 3, 4]
        payload = b"A" * self.payload_size

        for idx, aid in enumerate(algo_ids):
            self.progress.emit(idx + 1, len(algo_ids))
            name = ALGORITHM_NAMES.get(aid, f"Algo {aid}")
            log_emitter.emit(f"Benchmarking {name}...")

            try:
                algo_class = get_algorithm(aid)
                if aid in (0, 1, 2):
                    bits = {0: 1, 1: 2, 2: 3}.get(aid, 1)
                    algo = algo_class(bits=bits)
                else:
                    algo = algo_class()

                embed_start = time.perf_counter()
                stego = algo.embed(self.frames, payload)
                embed_time = time.perf_counter() - embed_start

                extract_start = time.perf_counter()
                extracted = algo.extract(stego, len(payload))
                extract_time = time.perf_counter() - extract_start

                diff = self.frames.astype(np.int16) - stego.astype(np.int16)
                mse = float(np.mean(diff ** 2))
                psnr = float('inf') if mse == 0 else float(20 * np.log10(255.0 / np.sqrt(mse)))

                extracted_bits = np.unpackbits(np.frombuffer(extracted, dtype=np.uint8))
                payload_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
                min_len = min(len(extracted_bits), len(payload_bits))
                ber = float(np.sum(payload_bits[:min_len] != extracted_bits[:min_len]) / min_len) if min_len > 0 else 0.0

                capacity = algo.capacity(self.frames)

                result = {
                    "algorithm_id": aid,
                    "algorithm_name": name,
                    "embedding_speed": len(payload) / embed_time if embed_time > 0 else 0,
                    "extraction_speed": len(payload) / extract_time if extract_time > 0 else 0,
                    "embedding_time": embed_time,
                    "extraction_time": extract_time,
                    "psnr": psnr,
                    "mse": mse,
                    "ber": ber,
                    "payload_capacity": capacity,
                }
                self.result_ready.emit(aid, result)
                self.results.append(result)

            except Exception as e:
                log_emitter.emit(f"  {name} failed: {str(e)}")
                result = {
                    "algorithm_id": aid,
                    "algorithm_name": name,
                    "embedding_speed": 0,
                    "extraction_speed": 0,
                    "embedding_time": 0,
                    "extraction_time": 0,
                    "psnr": 0,
                    "mse": 0,
                    "ber": 1.0,
                    "payload_capacity": 0,
                    "error": str(e),
                }
                self.result_ready.emit(aid, result)
                self.results.append(result)

        log_emitter.emit("Benchmark completed!")
        self.finished.emit(self.results)
