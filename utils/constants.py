MAGIC_NUMBER = b"STEG"

ALGORITHM_NAMES = {
    0: "Standard LSB 1-Bit",
    1: "Standard LSB 2-Bit",
    2: "Standard LSB 3-Bit",
    3: "Random LSB",
    4: "Adaptive LSB",
    5: "Edge-Based LSB",
    6: "LSBM",
    7: "LSBMR",
    8: "PVD",
    9: "BPCS",
    10: "OPAP",
    11: "PIT",
}

ALGORITHM_IDS = {v: k for k, v in ALGORITHM_NAMES.items()}

AUTO_DETECTION_ORDER = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
]

HEADER_SIZE_BYTES = 64

SUPPORTED_VIDEO_EXTENSIONS = [".mp4", ".mkv", ".avi", ".mov"]
SUPPORTED_AUDIO_EXTENSIONS = [".wav", ".mp3"]

VERSION = "1.0.0"
APP_NAME = "Spatial Domain Steganography"
