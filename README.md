# Automotive Multi-ECU CAN Network, Diagnostics and Validation Platform

**PROJECT 1 of 7** in an automotive embedded-systems portfolio (ENSA Khouribga, target: 2027 final-year internship).

A virtual (SIL-style) vehicle with six nodes on two CAN networks, a frozen CAN database,
CAPL simulation for Vector CANoe/CANalyzer, an academic UDS/OBD-II-inspired diagnostic subset,
fault injection, and a Python log-analysis/test layer.

> **Honesty statement.** Everything here is virtual/software-in-the-loop. Nothing has been validated on a
> real vehicle or ECU. Every test case carries an explicit status (see `tests/test_matrix.md`);
> no result is reported unless it was actually executed.
> This project is **not** AUTOSAR and does **not** claim ISO 14229 / ISO 26262 conformance.
> *AUTOSAR-inspired concepts are planned for future projects.*

## Status (Phase 1 delivered)
| Area | State |
|---|---|
| Requirements, architecture, CAN matrix, DBC spec | done (docs 01-05) |
| `vehicle_v1_0.dbc` (generated from `scripts/can_matrix.py`) | done, statically validated with `cantools` |
| E2E (counter + CRC-8) Python reference + unit tests | done, executed |
| CAPL: common libs + `powertrain_ecu.can` | written, **not yet compiled/run in CANoe** |
| Diagnostic / fault-injection / test specs | done (docs 06-08), designed only |
| Brake/BMS/Cluster/Gateway CAPL, diagnostics CAPL, injector, Python analysis | planned (Phases 2-6) |

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_dbc.py        # regenerate DBC/CSV/MD from the matrix source
python scripts/generate_dbc.py --check  # fail if committed files are stale
pytest -q                              # static DBC + E2E tests
```

## Layout
```
docs/           01..12 engineering documents (+ 00 overview/roadmap)
can_database/   vehicle_v1_0.dbc, can_matrix.csv, can_matrix.md (generated)
capl/           CAPL sources (common/*.cin + one node per ECU)
canoe/          CANoe configuration guide (no binary .cfg committed)
canalyzer/      CANalyzer analysis workflow
diagnostic/     pointer to diagnostic specification
python/         analysis layer (can_analysis, signal_processing, diagnostics, visualization, reporting)
tests/          unit tests + test matrix
results/        real results only (empty until executed)
scripts/        can_matrix.py (single source of truth), generate_dbc.py
```

## Frozen interfaces (reused by Projects 2-7)
ECU names, CAN IDs, signal names and the E2E profile are frozen at **DBC v1.0.0**.
Changes follow the policy in `docs/04_dbc_specification.md` (additive only; no renumbering).

## References (conceptual alignment only)
Vector CANoe <https://www.vector.com/fr/product/canoe/> - Vector CANalyzer <https://www.vector.com/fr/product/canalyzer/> -
AUTOSAR <https://www.autosar.org/> - MathWorks Model-Based Design <https://www.mathworks.com/help/simulink/gs/model-based-design.html> -
ISO 26262 <https://www.iso.org/standard/90020.html>
