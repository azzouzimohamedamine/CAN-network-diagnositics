# 07 - Fault Injection Plan

Injection is performed by a **separate** CAPL node (`fault_injection.can`, Phase 4) acting on a dedicated bus segment/CANoe interaction layer, never by code inside the ECUs (FLT-REQ-004).
Injection is reversible (FLT-REQ-002). Status of all rows: **designed, not executed**.

| Fault | Description | Detection mechanism | Expected ECU behaviour | DTC / NRC | Recovery | Test |
|---|---|---|---|---|---|---|
| F01 | Single missing CAN message (one 0x200 frame dropped) | Timeout counter < 3 x cycle -> not yet failed | No state change; no DTC (debounce) | none | none needed | TC-105 |
| F02 | CAN timeout (0x200 absent > 60 ms) | Cycle timeout 3 x 20 ms | PT -> DEGRADED, torque limited; CLUSTER `Warn_Brake`/`Warn_CommLoss` | U1100 (0x87) | Message returns: 5 good receptions heal testFailed; DTC stays confirmed until 0x14 | TC-104 |
| F03 | Invalid signal (VehicleSpeed = 0xFFFF) | Invalid-raw check | Value not used; PT holds last valid <= 500 ms then DEGRADED; cluster shows dashes | C1201 (0x86) | Valid value for 5 samples | TC-106 |
| F04 | Out-of-range value (BatteryVoltage = 600 V) | Plausibility vs DBC range | Value rejected; BMS_Fault / warn lamp | P1301 (0x86) | Back in range for 5 samples | TC-107 |
| F05 | ECU unavailable (BMS_ECU node stopped) | Timeouts of 0x300/0x301/0x302 | PT FAULT, torque 0; cluster `Warn_Battery`+`Warn_CommLoss` | U1101 | Node restart -> frames resume -> heal | TC-119 |
| F06 | Wrong message ID (frame with unlisted ID e.g. 0x6FF, or ID of another ECU's message) | GW allow-list; DBC ownership | GW drops, `GW_RoutingErrorCount++` | U1112 (GW) | n/a, stops when injection stops | TC-112 |
| F07a | Wrong alive counter (repeat/jump) | E2E counter check | Frame accepted or discarded per policy (discard); 3 failures confirm | U1110 (0x82) | 5 good frames | TC-108 |
| F07b | Wrong checksum (bit flip in payload) | CRC-8 mismatch | Frame discarded | U1111 (0x83) | 5 good frames | TC-109 |
| F08 | Invalid diagnostic request (bad length / unknown SID / DID) | Request parser | Negative response 0x13 / 0x11 / 0x31; no state change | NRC only (no DTC) | immediate | TC-114, TC-115 |

Safety note: these scenarios use ISO 26262 *vocabulary* informally; no ASIL rating or hazard analysis is claimed in Project 1 (Project 6).
