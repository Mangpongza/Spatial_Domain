class StegoModel:
    def __init__(self):
        self.algorithm_id: int = 0
        self.algorithm_name: str = ""
        self.lsb_mode: int = 1
        self.payload_size: int = 0
        self.audio_format: int = 0
        self.version: int = 1
        self.embedding_time: float = 0.0
        self.extraction_time: float = 0.0
        self.psnr: float = 0.0
        self.ssim: float = 0.0
        self.mse: float = 0.0
        self.ber: float = 0.0
        self.payload_capacity: int = 0
        self.payload_usage: float = 0.0

    def to_dict(self) -> dict:
        return {
            "algorithm_id": self.algorithm_id,
            "algorithm_name": self.algorithm_name,
            "lsb_mode": self.lsb_mode,
            "payload_size": self.payload_size,
            "audio_format": self.audio_format,
            "version": self.version,
            "embedding_time": self.embedding_time,
            "extraction_time": self.extraction_time,
            "psnr": self.psnr,
            "ssim": self.ssim,
            "mse": self.mse,
            "ber": self.ber,
            "payload_capacity": self.payload_capacity,
            "payload_usage": self.payload_usage,
        }
