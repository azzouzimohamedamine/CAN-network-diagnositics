# Test matrix (Phase 1)

Status legend: **E** = Executed-SW, **D** = Designed (not executed), see doc 08. "Actual" is filled only for executed tests.
Executed on 2026-11-12 with `pytest -q` (cantools strict loader): 17 test items passed, 0 failed (`tests/unit/test_dbc_static.py`, TC-005 and TC-008 are parametrized/looped).

| Test ID | Req. | Precondition | Stimulus | Expected | Actual | Result | Status |
|---|---|---|---|---|---|---|---|
| TC-001 | CAN-REQ-001 | DBC generated | cantools strict load | 21 messages, 6 nodes, no error | 21 messages, 6 nodes | PASS | E |
| TC-002 | CAN-REQ-002 | DBC loaded | check ID uniqueness, 11-bit, range ownership | all unique, owner matches range | as expected | PASS | E |
| TC-003 | CAN-REQ-004 | DBC loaded | encode/decode every signal at min and max | round trip within one LSB | as expected | PASS | E |
| TC-004 | CAN-REQ-012 | none | CRC-8 of "123456789" | 0x4B | 0x4B | PASS | E |
| TC-005 | CAN-REQ-011 | DBC loaded | check Counter 48/4 and Checksum 56/8 in 10 messages | present in all | as expected | PASS | E |
| TC-006 | CAN-REQ-003 | repo clean | regenerate and compare DBC/CSV/MD | identical | identical | PASS | E |
| TC-007 | CAN-REQ-004, -009 | matrix source | invalid raw outside valid raw range; receivers known | all signals | as expected | PASS | E |
| TC-008 | CAN-REQ-011, -013 | E2E module | protect, verify; flip bit; jump counter | OK / CRC_ERROR / COUNTER_ERROR | as expected | PASS | E |
| TC-101 | CAN-REQ-006 | CANoe, all nodes | 60 s run, PT_Status trace | mean 20 ms +/-10 % | not executed | - | D |
| TC-102 | CAN-REQ-006 | CANoe | 60 s run, PT_Torque | mean 10 ms +/-10 % | not executed | - | D |
| TC-103 | CAN-REQ-015 | CANoe/CANalyzer statistics | nominal run | bus load <= 40 % (analytical: 9.0 % / 6.9 % worst-case) | not executed (measured) | - | D |
| TC-104 | CAN-REQ-008, FLT F02 | BRAKE_ECU running | suppress 0x200 > 60 ms | timeout detected <= 60 ms + 1 cycle; DTC U1100 confirmed | not executed | - | D |
| TC-105 | FLT-REQ-005, F01 | as above | drop one 0x200 frame | no DTC | not executed | - | D |
| TC-106 | CAN-REQ-009, F03 | BRAKE_ECU | VehicleSpeed raw 0xFFFF | value unused, C1201, cluster dashes | not executed | - | D |
| TC-107 | CAN-REQ-010, F04 | BMS_ECU | BatteryVoltage 600 V | rejected, P1301 | not executed | - | D |
| TC-108 | CAN-REQ-013, F07a | any E2E msg | counter jump | U1110 after 3 failures | not executed | - | D |
| TC-109 | CAN-REQ-012, F07b | any E2E msg | flip payload bit | frame discarded, U1111 | not executed | - | D |
| TC-110 | GW-REQ-004, -005 | gateway running | 0x201 PT->INFO | latency <= 5 ms, payload identical | not executed | - | D |
| TC-111 | GW-REQ-002, -003 | gateway running | 0x101 on PT_CAN | not seen on INFO_CAN | not executed | - | D |
| TC-112 | GW-REQ-008, F06 | gateway running | inject ID 0x6FF | dropped, RoutingErrorCount++ | not executed | - | D |
| TC-113 | DIAG-REQ-009 | tester online | `22 F1 8C` to BMS | positive response | not executed | - | D |
| TC-114 | DIAG-REQ-004, F08 | tester online | SID 0x2F | `7F 2F 11` | not executed | - | D |
| TC-115 | DIAG-REQ-004, F08 | tester online | `19` with PCI length 1 | NRC 0x13 | not executed | - | D |
| TC-116 | DIAG-REQ-007 | after TC-104 | `19 02 08` | U1100, status 0x09 | not executed | - | D |
| TC-117 | DIAG-REQ-008 | DTC stored, extended session | `14 FF FF FF`, then `19 01` | `54`, count 0; default session -> NRC 0x7E | not executed | - | D |
| TC-118 | DIAG-REQ-005 | extended session | wait > 5 s | back to default session | not executed | - | D |
| TC-119 | FLT F05 | all nodes | stop BMS_ECU | U1101, PT FAULT, cluster lamps | not executed | - | D |
| TC-120 | TEST-REQ-005 | golden log (future) | Python analysis | identical statistics | not executed | - | D |
| TC-121 | CAN-REQ-004, -009 | DBC | SOC raw 1000 valid; 1001 out-of-range; 1023 invalid | classified correctly | not executed (receiver logic) | - | D |
| TC-901 | all | real vehicle / HIL | any | - | impossible without hardware | - | HW-unavailable |
