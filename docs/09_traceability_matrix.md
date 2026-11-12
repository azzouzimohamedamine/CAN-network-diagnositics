# 09 - Traceability Matrix (Requirement -> Design -> Implementation -> Test)

Implementation status: **done** (exists and executed), **written** (exists, not run in CANoe), **planned**.
| Requirement | Design | Implementation | Test | Impl. status |
|---|---|---|---|---|
| CAN-REQ-001 | 04 | `can_database/vehicle_v1_0.dbc` | TC-001 | done (CANoe import: not verified) |
| CAN-REQ-002 | 03, 04 | `scripts/can_matrix.py` | TC-002 | done |
| CAN-REQ-003 | 04 | `scripts/generate_dbc.py` | TC-006 | done |
| CAN-REQ-004, -005 | 04 | matrix + DBC | TC-003, TC-007, TC-121 | done / D |
| CAN-REQ-006 | 03, 05 | `capl/powertrain_ecu.can` (PT only) | TC-101, TC-102 | written |
| CAN-REQ-007 | 05 | BMS/cluster CAPL | (Phase 2 test) | planned |
| CAN-REQ-008 | 03, 05 | ECU supervision | TC-104 | planned |
| CAN-REQ-009, -010 | 05, 07 | ECU receivers | TC-106, TC-107, TC-121 | planned |
| CAN-REQ-011..013 | 03 | `e2e.py`, `e2e.cin` | TC-005, TC-004, TC-008, TC-108, TC-109 | done (Python) / written (CAPL) |
| CAN-REQ-014, -015 | 03 | `can_matrix.md` bus-load section | TC-103 | done (analysis) |
| GW-REQ-001..009 | 02, 05 | `gateway_ecu.can` | TC-110, TC-111, TC-112 | planned (Phase 3) |
| DIAG-REQ-001..010 | 06 | `diagnostics.can` | TC-113..TC-118 | planned (Phase 4); spec done |
| FLT-REQ-001..005 | 07 | `fault_injection.can` | TC-104..TC-109, TC-112, TC-114, TC-115, TC-119 | planned (Phase 4) |
| TEST-REQ-001..004 | 08 | `tests/test_matrix.md` | inspection | done |
| TEST-REQ-005 | 08 | `python/can_analysis` | TC-120 | planned (Phase 5) |
| SIM-REQ-001..003, ARCH-REQ-001..003, DOC-REQ-001 | 02, 11, 12 | docs | inspection | done |
Gaps are intentional and visible; they are the Phase 2-6 backlog.
