"""Parse Vector ASC logs (hex IDs, as exported by CANoe/CANalyzer by default) - classic CAN data frames only."""
import re
from dataclasses import dataclass

_ASC = re.compile(r"^\s*(\d+\.\d+)\s+(\d+)\s+([0-9A-Fa-f]+)x?\s+(Rx|Tx)\s+d\s+(\d+)((?:\s+[0-9A-Fa-f]{2})*)")


@dataclass(frozen=True)
class Frame:
    t: float
    channel: int
    can_id: int
    direction: str
    data: bytes


def parse_asc(lines):
    """Yield Frames; header/comment/other lines are ignored. Duplicate (time, channel, id, data) entries
    (the same frame logged as Tx and Rx) are collapsed."""
    seen = set()
    for line in lines:
        m = _ASC.match(line)
        if not m:
            continue
        dlc = int(m.group(5))
        data = bytes(int(x, 16) for x in m.group(6).split())[:dlc]
        f = Frame(float(m.group(1)), int(m.group(2)), int(m.group(3), 16), m.group(4), data)
        key = (f.t, f.channel, f.can_id, f.data)
        if key in seen:
            continue
        seen.add(key)
        yield f
