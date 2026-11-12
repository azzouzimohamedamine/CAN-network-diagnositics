# 01 - System Requirements Specification (v1.0)

Verification methods: **T** test (executed), **D** demonstration (CANoe run), **A** analysis, **I** inspection.
Status of verification is tracked in `09_traceability_matrix.md` and `../tests/test_matrix.md`.

## Scope
A virtual vehicle of six nodes (POWERTRAIN_ECU, BRAKE_ECU, BMS_ECU, CLUSTER_ECU, GATEWAY_ECU, DIAG_TESTER) on two virtual CAN networks
(PT_CAN, INFO_CAN). Software simulation only; no real-vehicle claims.

## CAN communication (CAN-REQ)
| ID | Requirement | Rationale | Ver. |
|---|---|---|---|
| CAN-REQ-001 | One DBC `vehicle_v1_0.dbc` shall define all messages/signals/nodes and load without error in cantools (strict) and CANoe. | Single reusable contract for Projects 2-7. | T, D |
| CAN-REQ-002 | All frames shall use 11-bit identifiers; ID ranges are owned per ECU (0x1xx PT, 0x2xx BRAKE, 0x3xx BMS, 0x4xx CLUSTER, 0x5xx GW, 0x6xx reserved for test/injection, 0x7xx diagnostics). | Prevents ID collisions when later projects add messages. | T |
| CAN-REQ-003 | DBC, CSV and Markdown matrix shall be generated from one source (`scripts/can_matrix.py`); stale files shall fail a test. | Avoids documentation/implementation drift. | T |
| CAN-REQ-004 | Every signal shall define start bit, length, byte order, factor, offset, physical range, unit and (where applicable) an invalid raw value. | Unambiguous encoding; supports plausibility checks. | I, T |
| CAN-REQ-005 | All application signals shall use Intel byte order. | One convention avoids decoding errors across tools. | I |
| CAN-REQ-006 | Cyclic messages shall be sent with the cycle time of the matrix within +/-10 % (mean) over a 60 s window. | Receivers' timeouts assume nominal periodicity. | D, A |
| CAN-REQ-007 | Event messages (BMS_Faults, CLUSTER_Warning) shall be sent within 10 ms of a state change and as a 500 ms heartbeat. | Fast fault propagation while keeping supervision possible. | D |
| CAN-REQ-008 | Receivers shall declare a message timed out after 3 x its cycle time without reception (heartbeat for event messages). | Tolerates one lost frame, detects real loss quickly. | D |
| CAN-REQ-009 | Signals carrying their invalid raw value shall be treated as "unavailable" by receivers and never used as physical values. | Prevents propagating sentinel values (e.g. 6553.5 V). | T, D |
| CAN-REQ-010 | Receivers shall plausibility-check decoded values against the physical range of the DBC. | Detects corruption that passes the CRC. | D |
| CAN-REQ-011 | Every application message (all except 0x7xx) shall carry a 4-bit alive counter at bit 48 and an 8-bit CRC at bit 56. | Detects frozen senders, corruption, replay. | T |
| CAN-REQ-012 | The CRC shall be CRC-8 SAE J1850 (poly 0x1D, init 0xFF, xorout 0xFF) over bytes 0-6. | Standard, documented algorithm with known check value. | T |
| CAN-REQ-013 | The alive counter shall increment by 1 per transmission modulo 16. | Simple sequence check. | T, D |
| CAN-REQ-014 | Both networks shall be specified at 500 kbit/s. | Single bit rate simplifies the first gateway. | I |
| CAN-REQ-015 | Nominal analytical bus load (worst-case stuffing) shall be <= 40 % per network. | Margin for event bursts and diagnostics. | A |

## Gateway (GW-REQ)
| ID | Requirement | Rationale | Ver. |
|---|---|---|---|
| GW-REQ-001 | GATEWAY_ECU shall connect PT_CAN and INFO_CAN. | Separates safety-relevant powertrain traffic from info/diagnostic port. | I, D |
| GW-REQ-002 | The gateway shall route only IDs on the allow-list in `can_matrix.md` (default deny). | Least-privilege routing. | D |
| GW-REQ-003 | 0x101 (PT->INFO) and 0x400/0x401/0x500 (INFO->PT) shall not be routed. | Demonstrates filtering. | D |
| GW-REQ-004 | Routing latency shall be <= 5 ms (measured at trace timestamps). | Keeps 10 ms signals usable on the destination bus. | D, A |
| GW-REQ-005 | Routed payloads shall be forwarded unmodified (E2E preserved end-to-end). | Receivers verify the original sender's protection. | D |
| GW-REQ-006 | Diagnostic requests 0x700-0x703 shall be routed INFO->PT; responses 0x709-0x70B PT->INFO. | Tester sits on the diagnostic port. | D |
| GW-REQ-007 | The gateway shall publish GW_Status (0x500) incl. bus load and routing error count. | Observability. | D |
| GW-REQ-008 | The gateway shall count frames with unknown IDs and never forward them. | Wrong-ID fault handling. | D |
| GW-REQ-009 | The gateway shall not create routing loops (a routed frame is never re-routed back). | Prevents bus flooding. | I, D |

## Diagnostics (DIAG-REQ)
| ID | Requirement | Rationale | Ver. |
|---|---|---|---|
| DIAG-REQ-001 | Implemented subset only: UDS 0x10, 0x3E, 0x22, 0x19 (01, 02), 0x14; OBD-II-inspired mode 0x01 PID 0x00/0x0D. | Honest, bounded scope. | I |
| DIAG-REQ-002 | Physical request/response IDs per ECU and a functional request 0x700; response ID = request ID + 8. | Frozen addressing for later projects. | T, D |
| DIAG-REQ-003 | Single-frame transport only (<= 7 payload bytes); ISO-TP is future work. | Keeps Phase 4 tractable. | I |
| DIAG-REQ-004 | Unsupported/invalid requests shall get a negative response (0x7F SID NRC) with NRC 0x11, 0x12, 0x13, 0x22, 0x31, 0x7E or 0x7F as specified. | Defined error behaviour. | D |
| DIAG-REQ-005 | Default and extended session; S3 timeout 5 s returns to default session. | Session concept. | D |
| DIAG-REQ-006 | P2 server response time <= 50 ms. | Timeout concept. | D |
| DIAG-REQ-007 | Each ECU shall store DTCs with status (testFailed, confirmed) per `06_diagnostics.md`. | DTC handling. | D |
| DIAG-REQ-008 | DTCs shall be readable (0x19) and clearable (0x14) in extended session only for clear. | Access control concept. | D |
| DIAG-REQ-009 | DIDs 0xF186, 0xF189, 0xF190 shall be readable (VIN is a simulated placeholder). | ECU identification. | D |
| DIAG-REQ-010 | Documentation shall state that ISO 14229 / ISO 15765 are NOT fully implemented. | Avoid overclaiming. | I |

## Fault management (FLT-REQ)
| ID | Requirement | Rationale | Ver. |
|---|---|---|---|
| FLT-REQ-001 | Eight fault scenarios F01-F08 shall be injectable (see doc 07). | Required coverage. | D |
| FLT-REQ-002 | Injection shall be reversible and leave no persistent change except stored DTCs. | Repeatable regression runs. | D |
| FLT-REQ-003 | Each fault shall map to a detection mechanism, DTC (or NRC) and recovery behaviour. | Traceable safety-style analysis (prepares Project 6). | I |
| FLT-REQ-004 | Injection code shall live in a separate node (`fault_injection.can`), absent from the nominal configuration. | ECU code must not contain test hooks. | I |
| FLT-REQ-005 | Errors shall be debounced: confirm after 3 consecutive failures; heal after 5 consecutive good receptions. | Avoid DTC flicker. | D |

## Test (TEST-REQ), simulation (SIM-REQ), architecture (ARCH-REQ), documentation (DOC-REQ)
| ID | Requirement | Rationale | Ver. |
|---|---|---|---|
| TEST-REQ-001 | At least 15 test cases shall be specified. | Coverage. | I |
| TEST-REQ-002 | Every requirement shall trace to at least one test or analysis. | Traceability. | I |
| TEST-REQ-003 | Each test shall carry a status: designed / executed (software) / simulated (CANoe SIL) / hardware-unavailable. | No false claims. | I |
| TEST-REQ-004 | No actual result shall be recorded unless produced by an executed run. | Integrity. | I |
| TEST-REQ-005 | A log-based Python workflow shall allow analysis without CANoe. | Student licence constraint. | T |
| SIM-REQ-001 | The project shall run without CAN hardware or a vehicle. | Student constraint. | I |
| SIM-REQ-002 | Results from virtual runs shall never be described as physical tests. | Integrity. | I |
| SIM-REQ-003 | Optional STM32/ESP32 hardware extension points shall be documented, not required. | Path to Project 2. | I |
| ARCH-REQ-001 | Software shall be layered: application / signal interface / E2E / diagnostics / fault management / configuration. | Maps to Projects 2 and 4. | I |
| ARCH-REQ-002 | ECU names and DBC naming shall follow the frozen conventions; changes follow the compatibility policy. | Continuity. | I, T |
| ARCH-REQ-003 | The project shall state it is not AUTOSAR. | Honesty. | I |
| DOC-REQ-001 | Documents 01-12 shall exist and stay consistent with the DBC. | Deliverable. | I |
