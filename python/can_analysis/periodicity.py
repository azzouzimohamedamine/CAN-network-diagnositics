"""Periodicity, missing-message and E2E analysis of a frame list against the vehicle DBC.
Pure analysis of a log - it never invents data. Event/diagnostic messages are not period-checked."""
import statistics
from collections import defaultdict
from dataclasses import dataclass, field

from . import e2e


@dataclass
class MsgReport:
    name: str
    can_id: int
    count: int
    cycle_ms: float
    mean_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0
    jitter_ms: float = 0.0
    period_ok: bool = True
    timeout_gaps: list = field(default_factory=list)      # (t_start, gap_ms) where gap > timeout
    crc_errors: int = 0
    counter_errors: int = 0
    checked: bool = True
    note: str = ""


def _attr(msg, key, default=None):
    try:
        return msg.dbc.attributes[key].value
    except (AttributeError, KeyError):
        return default


def analyze(frames, db, tolerance=0.10, channel=None):
    by_id = defaultdict(list)
    for f in frames:
        if channel is None or f.channel == channel:
            by_id[f.can_id].append(f)
    reports = []
    for can_id, fl in sorted(by_id.items()):
        try:
            msg = db.get_message_by_frame_id(can_id)
        except KeyError:
            reports.append(MsgReport(f"UNKNOWN_0x{can_id:03X}", can_id, len(fl), 0, checked=False,
                                     note="ID not in DBC"))
            continue
        cycle = float(_attr(msg, "GenMsgCycleTime", 0) or 0)
        send_type = int(_attr(msg, "GenMsgSendType", 1) or 0)      # 0 cyclic, 1 event, 2 cyclic+event
        timeout = float(_attr(msg, "MsgTimeoutMs", 0) or 0)
        r = MsgReport(msg.name, can_id, len(fl), cycle)
        times = [f.t for f in fl]
        gaps = [(b - a) * 1000.0 for a, b in zip(times, times[1:])]
        if gaps:
            r.mean_ms, r.min_ms, r.max_ms = statistics.mean(gaps), min(gaps), max(gaps)
            r.jitter_ms = statistics.pstdev(gaps)
        if cycle and timeout:
            r.timeout_gaps = [(times[i], g) for i, g in enumerate(gaps) if g > timeout]
            if send_type == 0 and gaps:
                r.period_ok = abs(r.mean_ms - cycle) <= tolerance * cycle
            elif send_type == 2:
                r.note = "cyclic+event: only max gap vs timeout is checked"
        else:
            r.checked = False
            r.note = "event/diagnostic message: no period check"
        if _attr(msg, "E2EProtected", 0) == 1:
            prev = None
            for f in fl:
                st = e2e.verify(f.data, prev)
                if st == e2e.E2EStatus.CRC_ERROR:
                    r.crc_errors += 1
                elif st == e2e.E2EStatus.COUNTER_ERROR:
                    r.counter_errors += 1
                prev = f.data[6] & 0x0F if len(f.data) == 8 else None
        reports.append(r)
    return reports


def format_report(reports):
    out = ["| Message | ID | Frames | Cycle ms | Mean ms | Min | Max | Jitter (std) | Period | Gaps > timeout | CRC err | Counter err |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in reports:
        if not r.checked:
            out.append(f"| {r.name} | 0x{r.can_id:03X} | {r.count} | - | - | - | - | - | n/a ({r.note}) | - | {r.crc_errors} | {r.counter_errors} |")
            continue
        per = "OK" if r.period_ok else "FAIL"
        out.append(f"| {r.name} | 0x{r.can_id:03X} | {r.count} | {r.cycle_ms:g} | {r.mean_ms:.2f} | {r.min_ms:.2f} | {r.max_ms:.2f} | "
                   f"{r.jitter_ms:.2f} | {per} | {len(r.timeout_gaps)} | {r.crc_errors} | {r.counter_errors} |")
    return "\n".join(out)
