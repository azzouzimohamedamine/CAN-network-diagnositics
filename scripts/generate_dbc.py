#!/usr/bin/env python3
"""Generate can_database/{vehicle_v1_0.dbc,can_matrix.csv,can_matrix.md} from can_matrix.py.
Usage: generate_dbc.py [--check]   (--check exits 1 if committed files are stale)"""
import csv, io, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import can_matrix as M

OUT = Path(__file__).resolve().parent.parent / "can_database"


def n(x):
    x = float(x)
    return str(int(x)) if x.is_integer() else repr(x)


def full_signals(m):
    sigs = list(m["signals"])
    if m["protected"]:
        sigs.append(M.sig(f"{m['name']}_Counter", 48, 4, hi=15, comment="E2E alive counter"))
        sigs.append(M.sig(f"{m['name']}_Checksum", 56, 8, hi=255, comment="E2E CRC-8 SAE J1850 over bytes 0-6"))
    return sigs


def validate():
    ids = set()
    for m in M.MESSAGES:
        assert m["id"] not in ids and m["id"] <= 0x7FF, m["name"]
        ids.add(m["id"])
        occ = set()
        for s in full_signals(m):
            bits = set(range(s["start"], s["start"] + s["length"]))
            assert not bits & occ, f"overlap {m['name']}.{s['name']}"
            assert s["start"] + s["length"] <= 8 * m["dlc"]
            occ |= bits
            rmin = -(1 << (s["length"] - 1)) if s["signed"] else 0
            rmax = (1 << (s["length"] - 1)) - 1 if s["signed"] else (1 << s["length"]) - 1
            lo_raw = round((s["lo"] - s["offset"]) / s["factor"])
            hi_raw = round((s["hi"] - s["offset"]) / s["factor"])
            assert rmin <= lo_raw <= hi_raw <= rmax, f"range {m['name']}.{s['name']}"
            if s["invalid"] is not None:
                assert rmin <= s["invalid"] <= rmax and not (lo_raw <= s["invalid"] <= hi_raw), \
                    f"invalid value {m['name']}.{s['name']}"
    for i, a, b in M.ROUTES:
        assert i in ids


def frame_bits(dlc, worst):
    base = 47 + 8 * dlc                     # SOF..IFS, no stuffing
    return base + ((34 + 8 * dlc - 1) // 4 if worst else 0)


def bus_load():
    res = {}
    byid = {m["id"]: m for m in M.MESSAGES}
    for bus in M.BUSES:
        fps = 0.0
        for m in M.MESSAGES:
            if m["cycle"] and m["bus"] == bus:
                fps += 1000.0 / m["cycle"]
        for i, _src, dst in M.ROUTES:
            if dst == bus and byid[i]["cycle"]:
                fps += 1000.0 / byid[i]["cycle"]
        res[bus] = (fps, [fps * frame_bits(8, w) / M.BITRATE * 100 for w in (False, True)])
    return res


def render_dbc():
    L = ['VERSION "%s"' % M.VERSION, "", "NS_ :", "\tCM_", "\tBA_DEF_", "\tBA_", "\tVAL_", "\tBA_DEF_DEF_", "",
         "BS_:", "", "BU_: " + " ".join(M.NODES), ""]
    for m in M.MESSAGES:
        L.append(f"BO_ {m['id']} {m['name']}: {m['dlc']} {m['sender']}")
        for s in full_signals(m):
            rx = ",".join(m["receivers"])
            L.append(f" SG_ {s['name']} : {s['start']}|{s['length']}@1{'-' if s['signed'] else '+'} "
                     f"({n(s['factor'])},{n(s['offset'])}) [{n(s['lo'])}|{n(s['hi'])}] \"{s['unit']}\" {rx}")
        L.append("")
    for m in M.MESSAGES:
        L.append(f'CM_ BO_ {m["id"]} "{m["comment"]}";')
        for s in full_signals(m):
            if s["comment"]:
                L.append(f'CM_ SG_ {m["id"]} {s["name"]} "{s["comment"]}";')
    L += ['BA_DEF_ "BusType" STRING ;', 'BA_DEF_ "DBName" STRING ;', 'BA_DEF_ "DBVersion" STRING ;',
          'BA_DEF_ BO_ "GenMsgCycleTime" INT 0 65535;',
          'BA_DEF_ BO_ "GenMsgSendType" ENUM "Cyclic","Event","CyclicAndEvent";',
          'BA_DEF_ BO_ "MsgTimeoutMs" INT 0 65535;',
          'BA_DEF_ BO_ "E2EProtected" ENUM "No","Yes";',
          'BA_DEF_ BO_ "OriginBus" STRING ;',
          'BA_DEF_ SG_ "SigInvalidRaw" INT 0 4294967295;',
          'BA_DEF_DEF_ "BusType" "CAN";', 'BA_DEF_DEF_ "DBName" "";', 'BA_DEF_DEF_ "DBVersion" "";',
          'BA_DEF_DEF_ "GenMsgCycleTime" 0;', 'BA_DEF_DEF_ "GenMsgSendType" "Event";',
          'BA_DEF_DEF_ "MsgTimeoutMs" 0;', 'BA_DEF_DEF_ "E2EProtected" "No";',
          'BA_DEF_DEF_ "OriginBus" "PT_CAN";', 'BA_DEF_DEF_ "SigInvalidRaw" 0;',
          'BA_ "BusType" "CAN";', 'BA_ "DBName" "vehicle";', f'BA_ "DBVersion" "{M.VERSION}";']
    for m in M.MESSAGES:
        L.append(f'BA_ "GenMsgCycleTime" BO_ {m["id"]} {m["cycle"] or 0};')
        L.append(f'BA_ "GenMsgSendType" BO_ {m["id"]} {["Cyclic", "Event", "CyclicAndEvent"].index(m["send_type"])};')
        L.append(f'BA_ "MsgTimeoutMs" BO_ {m["id"]} {m["timeout"] or 0};')
        L.append(f'BA_ "E2EProtected" BO_ {m["id"]} {1 if m["protected"] else 0};')
        L.append(f'BA_ "OriginBus" BO_ {m["id"]} "{m["bus"]}";')
        for s in full_signals(m):
            if s["invalid"] is not None:
                L.append(f'BA_ "SigInvalidRaw" SG_ {m["id"]} {s["name"]} {s["invalid"]};')
    for m in M.MESSAGES:
        for s in full_signals(m):
            if s["enum"]:
                vals = " ".join(f'{k} "{v}"' for k, v in sorted(s["enum"].items(), reverse=True))
                L.append(f'VAL_ {m["id"]} {s["name"]} {vals} ;')
    return "\n".join(L) + "\n"


def render_csv():
    o = io.StringIO()
    w = csv.writer(o, lineterminator="\n")
    w.writerow(["can_id", "message", "dlc", "sender", "receivers", "origin_bus", "send_type", "cycle_ms",
                "timeout_ms", "signal", "start_bit", "length", "byte_order", "signed", "factor", "offset",
                "phys_min", "phys_max", "unit", "invalid_raw", "values"])
    for m in M.MESSAGES:
        for s in full_signals(m):
            w.writerow([f"0x{m['id']:03X}", m["name"], m["dlc"], m["sender"], " ".join(m["receivers"]), m["bus"],
                        m["send_type"], m["cycle"] or "", m["timeout"] or "", s["name"], s["start"], s["length"],
                        "Intel", "signed" if s["signed"] else "unsigned", n(s["factor"]), n(s["offset"]),
                        n(s["lo"]), n(s["hi"]), s["unit"], "" if s["invalid"] is None else s["invalid"],
                        ";".join(f"{k}={v}" for k, v in sorted((s["enum"] or {}).items()))])
    return o.getvalue()


def render_md():
    L = [f"# CAN matrix v{M.VERSION} (GENERATED - do not edit; edit scripts/can_matrix.py)", "",
         f"Both networks: {M.BITRATE // 1000} kbit/s, 11-bit identifiers, DLC 8, Intel byte order.", "",
         "## Messages", "", "| ID | Name | Sender | Receivers | Origin bus | Type | Cycle ms | Timeout ms | E2E |",
         "|---|---|---|---|---|---|---|---|---|"]
    for m in M.MESSAGES:
        L.append(f"| 0x{m['id']:03X} | {m['name']} | {m['sender']} | {', '.join(m['receivers'])} | {m['bus']} | "
                 f"{m['send_type']} | {m['cycle'] or '-'} | {m['timeout'] or '-'} | {'yes' if m['protected'] else 'no'} |")
    L += ["", "## Signals (application messages)", "",
          "| Message | Signal | Start|Len | Signed | Factor | Offset | Range | Unit | Invalid raw | Values |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for m in M.MESSAGES:
        if not m["protected"]:
            continue
        for s in full_signals(m):
            vals = ", ".join(f"{k}={v}" for k, v in sorted((s["enum"] or {}).items()))
            L.append(f"| {m['name']} | {s['name']} | {s['start']}|{s['length']} | {'Y' if s['signed'] else 'N'} | "
                     f"{n(s['factor'])} | {n(s['offset'])} | {n(s['lo'])}..{n(s['hi'])} | {s['unit']} | "
                     f"{'' if s['invalid'] is None else s['invalid']} | {vals} |")
    L += ["", "## Diagnostic messages", "", "Raw single-frame payload: `PCI(0|8) SID(8|8) Data(16|48)`. Response ID = request ID + 0x08 "
          "(0x708 reserved: no functional response)."]
    L += ["", "## Gateway routing allow-list (default deny)", "", "| CAN ID | Name | From | To |", "|---|---|---|---|"]
    byid = {m["id"]: m["name"] for m in M.MESSAGES}
    for i, a, b in M.ROUTES:
        L.append(f"| 0x{i:03X} | {byid[i]} | {a} | {b} |")
    L += ["", "## Theoretical bus load (ANALYTICAL - not measured)", "",
          "Nominal periodic traffic only (event bursts and diagnostics excluded), 8-byte standard frames: "
          f"{frame_bits(8, False)} bit/frame without stuffing, {frame_bits(8, True)} bit/frame worst-case stuffing.", "",
          "| Bus | Frames/s | Load, no stuffing | Load, worst-case stuffing |", "|---|---|---|---|"]
    for bus, (fps, (a, b)) in bus_load().items():
        L.append(f"| {bus} | {fps:.0f} | {a:.1f} % | {b:.1f} % |")
    return "\n".join(L) + "\n"


def main():
    validate()
    files = {"vehicle_v1_0.dbc": render_dbc(), "can_matrix.csv": render_csv(), "can_matrix.md": render_md()}
    if "--check" in sys.argv:
        bad = [f for f, t in files.items() if not (OUT / f).exists() or (OUT / f).read_text() != t]
        print("STALE: " + ", ".join(bad) if bad else "up to date")
        sys.exit(1 if bad else 0)
    for f, t in files.items():
        (OUT / f).write_text(t)
        print("wrote", OUT / f)


if __name__ == "__main__":
    main()
