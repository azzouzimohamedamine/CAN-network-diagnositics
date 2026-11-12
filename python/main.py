"""Entry point of the analysis layer. Phase 1 provides only `dbc-summary`; analysis commands arrive in Phase 5."""
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
    print("usage: main.py dbc-summary   (analysis commands: Phase 5, not implemented)")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
