"""Static validation of the vehicle DBC and the E2E reference (TC-001..TC-007). No CANoe needed."""
from pathlib import Path
import cantools
import pytest
import can_matrix as M
import generate_dbc as G
from can_analysis import e2e

ROOT = Path(__file__).resolve().parents[2]
DB = cantools.database.load_file(ROOT / "can_database" / "vehicle_v1_0.dbc", strict=True)
PROTECTED = [m for m in M.MESSAGES if m["protected"]]


def test_tc001_dbc_loads_strict_and_matches_matrix():
    assert {m.name for m in DB.messages} == {m["name"] for m in M.MESSAGES}
    assert {n.name for n in DB.nodes} == set(M.NODES)


def test_tc002_ids_unique_standard_and_owned_by_range():
    ids = [m.frame_id for m in DB.messages]
    assert len(ids) == len(set(ids))
    owner = {1: M.PT, 2: M.BR, 3: M.BMS, 4: M.CL, 5: M.GW}
    for m in DB.messages:
        assert not m.is_extended_frame and m.frame_id <= 0x7FF
        if m.frame_id >> 8 in owner:
            assert m.senders == [owner[m.frame_id >> 8]], m.name


def test_tc003_roundtrip_min_and_max_of_every_signal():
    for m in DB.messages:
        for pick in ("minimum", "maximum"):
            data = {s.name: getattr(s, pick) for s in m.signals}
            dec = m.decode(m.encode(data, strict=True), decode_choices=False)
            for s in m.signals:
                assert dec[s.name] == pytest.approx(data[s.name], abs=abs(s.scale)), (m.name, s.name, pick)


def test_tc004_crc8_reference_check_value():
    assert e2e.crc8(b"123456789") == 0x4B


@pytest.mark.parametrize("m", PROTECTED, ids=lambda m: m["name"])
def test_tc005_e2e_layout_in_every_protected_message(m):
    dm = DB.get_message_by_name(m["name"])
    c, k = dm.get_signal_by_name(m["name"] + "_Counter"), dm.get_signal_by_name(m["name"] + "_Checksum")
    assert (c.start, c.length) == (48, 4) and (k.start, k.length) == (56, 8)


def test_tc006_generated_files_not_stale():
    G.validate()
    for f, text in (("vehicle_v1_0.dbc", G.render_dbc()), ("can_matrix.csv", G.render_csv()), ("can_matrix.md", G.render_md())):
        assert (ROOT / "can_database" / f).read_text() == text


def test_tc007_receivers_known_and_invalid_values_outside_valid_range():
    for m in M.MESSAGES:
        assert set(m["receivers"]) <= set(M.NODES) and m["sender"] not in m["receivers"]
    G.validate()  # asserts invalid raw is outside [phys_min, phys_max] raw range


def test_tc008_e2e_protect_verify_detects_bitflip_and_counter_jump():
    for m in PROTECTED:
        dm = DB.get_message_by_name(m["name"])
        f = bytearray(dm.encode({s.name: s.minimum for s in dm.signals if "_Counter" not in s.name and "_Checksum" not in s.name} |
                                {m["name"] + "_Counter": 0, m["name"] + "_Checksum": 0}))
        e2e.protect(f, 5)
        assert e2e.verify(bytes(f), prev_counter=4) == e2e.E2EStatus.OK
        assert e2e.verify(bytes(f), prev_counter=9) == e2e.E2EStatus.COUNTER_ERROR
        f[2] ^= 0x10
        assert e2e.verify(bytes(f)) == e2e.E2EStatus.CRC_ERROR
