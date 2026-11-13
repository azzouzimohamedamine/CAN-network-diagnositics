"""Tests of the log-analysis code on SYNTHETIC logs generated here (not CANoe measurements)."""
from pathlib import Path
import cantools
from can_analysis import e2e
from can_analysis.asc_log import parse_asc
from can_analysis.periodicity import analyze

ROOT = Path(__file__).resolve().parents[2]
DB = cantools.database.load_file(ROOT / "can_database" / "vehicle_v1_0.dbc", strict=True)
PT = DB.get_message_by_name("PT_Status")


def make_asc(duration_s=2.0, drop=(), bad_crc_at=None, counter_jump_at=None, period=0.020):
    """Synthetic ASC text for PT_Status; drop = (t_from, t_to) window without frames."""
    base = {s.name: 0 for s in PT.signals}
    lines = ["date Fri Nov 13 10:00:00 am 2026", "base hex  timestamps absolute", "Begin TriggerBlock"]
    n, cnt = 0, 0
    while n * period <= duration_s:
        t = n * period
        n += 1
        cnt = (cnt + 1) & 0xF
        if counter_jump_at is not None and n == counter_jump_at:
            cnt = (cnt + 5) & 0xF
        if drop and drop[0] <= t < drop[1]:
            continue
        data = bytearray(PT.encode(base | {"PT_Status_Counter": 0, "PT_Status_Checksum": 0}))
        e2e.protect(data, cnt)
        if bad_crc_at is not None and n == bad_crc_at:
            data[7] ^= 0xFF
        lines.append(f"   {t:.6f} 1  100             Tx   d 8 " + " ".join(f"{b:02X}" for b in data) + "  Length = 0 BitCount = 0")
    lines.append("End TriggerBlock")
    return lines


def rep(lines, name="PT_Status"):
    return {r.name: r for r in analyze(list(parse_asc(lines)), DB)}[name]


def test_tc201_nominal_period_ok_no_errors():
    r = rep(make_asc())
    assert r.count > 95 and r.period_ok and abs(r.mean_ms - 20) < 0.1
    assert r.timeout_gaps == [] and r.crc_errors == 0 and r.counter_errors == 0


def test_tc202_missing_window_detected_as_timeout_gap():
    r = rep(make_asc(drop=(1.0, 1.2)))            # 200 ms outage > 60 ms timeout
    assert len(r.timeout_gaps) == 1 and r.timeout_gaps[0][1] > 200 - 1


def test_tc203_single_dropped_frame_is_not_a_timeout():
    r = rep(make_asc(drop=(1.0, 1.015)))          # one 20 ms frame lost -> gap 40 ms < 60 ms
    assert r.timeout_gaps == []


def test_tc204_wrong_period_fails_period_check():
    assert not rep(make_asc(period=0.030)).period_ok


def test_tc205_crc_and_counter_errors_counted():
    assert rep(make_asc(bad_crc_at=10)).crc_errors == 1
    assert rep(make_asc(counter_jump_at=10)).counter_errors >= 1


def test_tc206_unknown_id_reported():
    lines = make_asc()[:3] + ["   0.010000 1  6FF             Tx   d 8 00 00 00 00 00 00 00 00"]
    assert [r for r in analyze(list(parse_asc(lines)), DB) if r.name.startswith("UNKNOWN")]
