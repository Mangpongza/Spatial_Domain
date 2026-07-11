import struct
from utils.constants import MAGIC_NUMBER, HEADER_SIZE_BYTES
from utils.crc import compute_crc32

HEADER_SIZE = HEADER_SIZE_BYTES
HEADER_FORMAT = "<4sBBBIII45x"

# Layout (64 bytes total):
#   Magic Number (4B) - b"STEG"
#   Version (1B)
#   Algorithm ID (1B)
#   LSB Mode (1B)
#   Payload Size (4B) - uint32
#   Audio Format (4B) - uint32
#   Checksum CRC32 (4B) - uint32
#   Padding (45B) to make 64 bytes


def build_header(
    algorithm_id: int,
    lsb_mode: int,
    payload_size: int,
    audio_format: int,
    version: int = 1,
) -> bytes:
    raw = struct.pack(
        HEADER_FORMAT,
        MAGIC_NUMBER,
        version,
        algorithm_id,
        lsb_mode,
        payload_size,
        audio_format,
        0,
    )
    crc = compute_crc32(raw)
    raw = struct.pack(
        HEADER_FORMAT,
        MAGIC_NUMBER,
        version,
        algorithm_id,
        lsb_mode,
        payload_size,
        audio_format,
        crc,
    )
    return raw


def parse_header(data: bytes) -> dict | None:
    struct_size = struct.calcsize(HEADER_FORMAT)
    if len(data) < struct_size:
        return None
    try:
        magic, version, algo_id, lsb_mode, payload_size, audio_fmt, crc_stored = (
            struct.unpack(HEADER_FORMAT, data[:struct_size])
        )
    except struct.error:
        return None
    if magic != MAGIC_NUMBER:
        return None
    temp = struct.pack(
        HEADER_FORMAT,
        MAGIC_NUMBER,
        version,
        algo_id,
        lsb_mode,
        payload_size,
        audio_fmt,
        0,
    )
    if compute_crc32(temp) != crc_stored:
        return None
    return {
        "magic": magic,
        "version": version,
        "algorithm_id": algo_id,
        "lsb_mode": lsb_mode,
        "payload_size": payload_size,
        "audio_format": audio_fmt,
        "crc": crc_stored,
    }
