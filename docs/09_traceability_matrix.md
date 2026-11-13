# 09 - Traceability Matrix (Requirement -> Design -> Implementation -> Test)

Implementation status: **done** (exists and executed), **written** (exists, not run in CANoe), **planned**.
| Requirement | Design | Implementation | Test | Impl. status |
|---|---|---|---|---|
| CAN-REQ-001 | 04 | `can_database/vehicle_v1_0.dbc` | TC-001 | done (CANoe import: not verified) |
| CAN-REQ-002 | 03, 04 | `scripts/can_matrix.py` | TC-002 | done |
| CAN-REQ-003 | 04 | `scripts/generate_dbc.py` | TC-006 | done |
| CAN-REQ-004, -005 | 04 | matrix + DBC | TC-003, TC-007, TC-121 | done / D |
| CAN-REQ-006 | 03, 05 | PT/BRAKE/BMS/CLUSTER CAPL; `periodicity.py` | TC-101, TC-102, TC-201, TC-204, TC-211 | written; analysis done |
| CAN-REQ-007 | 05 | `bms_ecu.can`, `cluster_ecu.can` (SendFault/SendWarn) | TC-212 | written (Phase 2) |
| CAN-REQ-008 | 03, 05 | `common/supervision.cin` (Mon_Tick) in PT/BRAKE/BMS/CLUSTER | TC-104, TC-202, TC-215, TC-216 | written (Phase 2); log analysis done |
| CAN-REQ-009, -010 | 05, 07 | `Sig_Check` in supervision.cin, PT/CLUSTER handlers | TC-106, TC-107, TC-121, TC-218 | written (Phase 2) |
| CAN-REQ-011..013 | 03 | `e2e.py`, `e2e.cin` | TC-005, TC-004, TC-008, TC-108, TC-109 | done (Python) / written (CAPL) |
| CAN-REQ-014, -015 | 03 | `can_matrix.md` bus-load section | TC-103 | done (analysis) |
| GW-REQ-001..009 | 02, 05 | `gateway_ecu.can` | TC-110, TC-111, TC-112 | planned (Phase 3) |
| DIAG-REQ-001..010 | 06 | `diagnostics.can` | TC-113..TC-118 | planned (Phase 4); spec done |
| FLT-REQ-005 (debounce) | 07 | `supervision.cin`, `sil/supervision.py` | TC-105, TC-203, TC-302, TC-305, TC-306 | written (CAPL); executed in SIL |
| FLT-REQ-001..003 (F01-F05, F07) in SIL | 07 | `sil/scenarios.py` | TC-302..TC-308 | executed (simulated) |
| FLT-REQ-001..004 | 07 | `fault_injection.can` | TC-104..TC-109, TC-112, TC-114, TC-115, TC-119 | planned (Phase 4) |
| TEST-REQ-001..004 | 08 | `tests/test_matrix.md` | inspection | done |
| TEST-REQ-005 | 08 | `python/can_analysis` | TC-120 | planned (Phase 5) |
| SIM-REQ-001..003, ARCH-REQ-001..003, DOC-REQ-001 | 02, 11, 12 | docs | inspection | done |
Gaps are intentional and visible; they are the Phase 2-6 backlog.
