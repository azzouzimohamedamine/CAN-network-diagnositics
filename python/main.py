"""Entry point of the analysis layer: `dbc-summary`, `periodicity <log.asc>`, `sil <scenario|all>` (Phase 2). Plots/report: Phase 5."""
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
    if argv[:1] == ["sil"] and len(argv) >= 2:
        from sil.scenarios import SCENARIOS, run
        from can_analysis.asc_log import parse_asc
        from can_analysis.periodicity import analyze, format_report
        db = cantools.database.load_file(DBC, strict=True)
        out = DBC.parent.parent / "results" / "sil"
        out.mkdir(parents=True, exist_ok=True)
        for name in (SCENARIOS if argv[1] == "all" else [argv[1]]):
            r = run(name)
            path = out / f"{name}.asc"
            r.sim.write_asc(path)
            print(f"\n=== {name} (SIMULATED, Python SIL) -> {path}")
            for t, owner, text in r.sim.events:
                print(f"  {t:6d} ms  {owner:<15} {text}")
            if len(argv) > 2 and argv[2] == "--report":
                with open(path) as fh:
                    print(format_report(analyze(list(parse_asc(fh)), db)))
        return 0
    if argv[:1] == ["sil-report"]:
        from reporting.sil_report import build
        root = DBC.parent.parent
        (root / "docs" / "figures").mkdir(parents=True, exist_ok=True)
        build(root / "docs" / "figures", root / "docs" / "sil_results.md")
        print("wrote docs/sil_results.md and docs/figures/sil_*.png")
        return 0
    print("usage: main.py dbc-summary | periodicity <log.asc> | sil <scenario|all> [--report] | sil-report")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
