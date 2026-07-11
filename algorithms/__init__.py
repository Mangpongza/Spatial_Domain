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
    from algorithms.EdgeBasedLSB import EdgeBasedLSB
    from algorithms.LSBM import LSBM
    from algorithms.LSBMR import LSBMR
    from algorithms.PVD import PVD
    from algorithms.BPCS import BPCS
    from algorithms.OPAP import OPAP
    from algorithms.PIT import PIT

    mapping = {
        0: StandardLSB,
        1: StandardLSB,
        2: StandardLSB,
        3: RandomLSB,
        4: AdaptiveLSB,
        5: EdgeBasedLSB,
        6: LSBM,
        7: LSBMR,
        8: PVD,
        9: BPCS,
        10: OPAP,
        11: PIT,
    }
    return mapping[algorithm_id]
