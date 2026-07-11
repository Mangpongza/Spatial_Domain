from abc import ABC, abstractmethod
import numpy as np


class BaseStegoAlgorithm(ABC):
    algorithm_id: int
    algorithm_name: str
    lsb_mode: int = 1

    @abstractmethod
    def embed(self, frames: np.ndarray, payload: bytes) -> np.ndarray:
        pass

    @abstractmethod
    def extract(self, frames: np.ndarray, payload_size: int) -> bytes:
        pass

    @abstractmethod
    def capacity(self, frames: np.ndarray) -> int:
        pass

    @abstractmethod
    def analyze(self, original: np.ndarray, modified: np.ndarray) -> dict:
        pass


def get_algorithm(algorithm_id: int) -> type[BaseStegoAlgorithm]:
    from algorithms.StandardLSB import StandardLSB
    from algorithms.RandomLSB import RandomLSB
    from algorithms.AdaptiveLSB import AdaptiveLSB

    mapping = {
        0: StandardLSB,
        1: StandardLSB,
        2: StandardLSB,
        3: RandomLSB,
        4: AdaptiveLSB,
    }
    return mapping[algorithm_id]
