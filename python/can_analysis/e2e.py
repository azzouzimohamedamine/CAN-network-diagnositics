"""E2E reference implementation (counter + CRC-8) shared by tests and log analysis.

Profile "VEH-E2E-1" (frozen with DBC v1.0.0):
  byte 6 bits 0-3 : alive counter (0..15, wraps)      -> DBC <MSG>_Counter  48|4
  byte 7          : CRC-8 SAE J1850 over bytes 0..6   -> DBC <MSG>_Checksum 56|8
  CRC parameters  : poly 0x1D, init 0xFF, no reflection, xorout 0xFF (check value for "123456789" = 0x4B)
Engineering-style, inspired by E2E concepts; NOT the AUTOSAR E2E library.
"""
from enum import Enum


class E2EStatus(Enum):
    OK = "OK"
    CRC_ERROR = "CRC_ERROR"
    COUNTER_ERROR = "COUNTER_ERROR"


def crc8(data: bytes, init: int = 0xFF, poly: int = 0x1D, xorout: int = 0xFF) -> int:
    crc = init
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ poly) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc ^ xorout


def frame_crc(frame: bytes) -> int:
    return crc8(bytes(frame[:7]))


def protect(frame: bytearray, counter: int) -> bytearray:
    frame[6] = (frame[6] & 0xF0) | (counter & 0x0F)
    frame[7] = frame_crc(frame)
    return frame


def verify(frame: bytes, prev_counter=None) -> E2EStatus:
    if len(frame) != 8 or frame[7] != frame_crc(frame):
        return E2EStatus.CRC_ERROR
    if prev_counter is not None and (frame[6] & 0x0F) != ((prev_counter + 1) & 0x0F):
        return E2EStatus.COUNTER_ERROR
    return E2EStatus.OK
