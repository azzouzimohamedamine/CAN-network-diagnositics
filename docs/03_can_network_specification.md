# 03 - CAN Network Specification

The authoritative tables are generated: **`../can_database/can_matrix.md`** (messages, signals, routing, bus load) and `can_matrix.csv`.
This document explains the engineering reasoning.

## CAN fundamentals (as applied here)
| Concept | Reasoning in this project |
|---|---|
| Frame / identifier | 11-bit base frames. The ID is both a label and the **priority**: lower ID wins arbitration. Safety-relevant, fast messages (powertrain 0x1xx, brake 0x2xx) therefore get lower IDs than cluster/gateway status; diagnostics (0x7xx) lose arbitration against everything, so they can never starve control traffic. |
| Arbitration | Bitwise, non-destructive: dominant 0 overrides recessive 1. Worst-case latency of a frame = its own transmission + one blocking frame already on the bus + higher-priority traffic. |
| DLC / data | All application frames use DLC 8 to leave room for E2E bytes and future signals (reserved bits stay 0). Fixed DLC simplifies DBC compatibility. |
| CRC / ACK | The 15-bit CAN hardware CRC and ACK slot are handled by the controller; CANoe virtual channels do not model them. The **application CRC-8** (byte 7) protects against corruption that bypasses link layer checks (e.g. gateway memory errors) and is what we can inject faults into. |
| Error handling | CAN controllers do error frames / TEC-REC counters / bus-off. Not modelled in virtual channels (limitation, doc 11). Application-level supervision (timeouts, E2E, plausibility) is what we implement. |
| Periodicity | Fixed cycles (10/20/50/100 ms) plus two event messages with 500 ms heartbeat. Cycle choice follows signal dynamics: speed/torque 10 ms, brake 20 ms, battery 50-100 ms. |
| Bus load | Computed analytically from the matrix (see `can_matrix.md`; frame = 111 bit nominal, 135 bit with worst-case stuffing). Budget 40 %. Measured values are produced only by CANalyzer/CANoe runs and stored in `results/`. |
| Signal encoding | Physical = raw x factor + offset. Raw width chosen from required resolution (e.g. SOC 0.1 % -> 10 bit). Each signal reserves one raw value as **invalid** (all-ones or 0x7FFF for signed) outside the valid range. |
| Filtering | Receivers accept only IDs they subscribe to (DBC receiver list); the gateway applies a default-deny allow-list. |
| Timeout monitoring | 3 x cycle (heartbeat for event messages): one lost frame is tolerated, two consecutive losses at the third period are flagged. Examples: 0x201 -> 30 ms, 0x200 -> 60 ms, 0x300 -> 300 ms, 0x302 -> 1500 ms. |

## Networks and routing
`PT_CAN`: 0x100, 0x101, 0x200, 0x201, 0x300, 0x301, 0x302, diagnostic responses 0x709-0x70B.
`INFO_CAN`: 0x400, 0x401, 0x500, diagnostic requests, plus routed copies (allow-list in `can_matrix.md`).

## E2E profile VEH-E2E-1
Counter: byte 6 bits 0-3. CRC: byte 7 = CRC-8 SAE J1850 (poly 0x1D, init 0xFF, xorout 0xFF) over bytes 0-6.
Bits 52-55 are reserved (0). Reference implementation: `python/can_analysis/e2e.py`; CAPL: `capl/common/e2e.cin`.
Receiver behaviour: CRC error -> discard frame, count failure; counter error (not previous+1) -> count failure; 3 consecutive failures -> DTC (see doc 06/07).

## Reserved ranges for later projects
0x210-0x21F ADAS/AEB (Project 3), 0x310-0x33F BMS extensions (SOC/SOH/RUL detail, Project 5), 0x600-0x6FF test/injection.
