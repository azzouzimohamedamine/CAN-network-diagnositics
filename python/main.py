"""Entry point of the analysis layer: `dbc-summary`, `periodicity <log.asc>` (Phase 2). Plots/report: Phase 5."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sys
from pathlib import Path
import cantools

DBC = Path(__file__).resolve().parent.parent / "can_database" / "vehicle_v1_0.dbc"


def main(argv):
    if argv[:1] == ["dbc-summary"]:
        db = cantools.database.load_file(DBC, strict=True)
        for m in sorted(db.messages, key=lambda m: m.frame_id):
            print(f"0x{m.frame_id:03X} {m.name:<24} {len(m.signals):>2} signals  sender={m.senders[0]}")
        return 0
    if argv[:1] == ["periodicity"] and len(argv) >= 2:
        from can_analysis.asc_log import parse_asc
        from can_analysis.periodicity import analyze, format_report
        db = cantools.database.load_file(DBC, strict=True)
        with open(argv[1], errors="replace") as fh:
            frames = list(parse_asc(fh))
        print(f"{len(frames)} frames parsed from {argv[1]}")
        print(format_report(analyze(frames, db)))
        return 0
    print("usage: main.py dbc-summary | periodicity <log.asc>")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
