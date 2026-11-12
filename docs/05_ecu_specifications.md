# 05 - ECU Specifications

Message/signal details: `../can_database/can_matrix.md`. Timeouts = 3 x cycle. "Debounce" = FLT-REQ-005 (confirm after 3 failures, heal after 5 good).

## POWERTRAIN_ECU (PT_CAN) - physical diag 0x701 / 0x709
| Item | Specification |
|---|---|
| Purpose | Drive state machine (OFF/INIT/READY/DRIVE/DEGRADED/FAULT), torque control placeholder. |
| TX | PT_Status 0x100 (20 ms), PT_Torque 0x101 (10 ms). |
| RX | BRAKE_Status 0x200 (60 ms timeout), BRAKE_VehicleDynamics 0x201 (30 ms), BMS_Status 0x300 (300 ms), BMS_Measurements 0x301 (150 ms), BMS_Faults 0x302 (1500 ms). |
| Error behaviour | 0x200 or brake signal invalid -> torque limited/zero, state DEGRADED. BMS timeout/critical fault -> torque request forced to 0, state FAULT. Invalid VehicleSpeed -> use last valid value for <= 500 ms then DEGRADED. |
| Diagnostics | DTC U1100 (lost BRAKE_ECU), U1101 (lost BMS_ECU), U1110/U1111 (E2E), C1201 (VehicleSpeed invalid); DIDs F186/F189/F18C. |
| Status | TX implemented in CAPL (not compiled); RX/supervision Phase 2-3. |

## BRAKE_ECU (PT_CAN) - 0x702 / 0x70A
| Purpose | Brake status, pedal/pressure, VehicleSpeed (wheel-derived), acceleration, yaw rate. |
| TX | BRAKE_Status 0x200 (20 ms), BRAKE_VehicleDynamics 0x201 (10 ms). |
| RX | PT_Status 0x100 (60 ms timeout, informational). |
| Error behaviour | Sensor fault -> `BrakeSystemFault=1`, `BrakeStatus=FAULT`, speed signals set to invalid raw; never transmits plausible-but-wrong values. |
| Diagnostics | Own plausibility DTC C1201 (speed sensor), U1102 (lost POWERTRAIN_ECU). |

## BMS_ECU (PT_CAN) - 0x703 / 0x70B
| Purpose | Battery state, SOC/SOH, pack measurements, fault events. Reused by Project 5. |
| TX | BMS_Status 0x300 (100 ms), BMS_Measurements 0x301 (50 ms), BMS_Faults 0x302 (event + 500 ms). |
| RX | PT_Torque 0x101 (30 ms) for current-demand awareness. |
| Error behaviour | Voltage/temperature/current limit violation -> BMS_Fault + severity, contactors open on CRITICAL. Sensor invalid -> invalid raw + `SENSOR_INVALID`. |
| Diagnostics | DTC P1301 (BatteryVoltage range), P1302 (BatteryTemperature), P1303 (BatteryCurrent), U1102. |

## CLUSTER_ECU (INFO_CAN) - 0x705 / 0x70D
| Purpose | Display speed/SOC, warning lamps, supervision of routed traffic. |
| TX | CLUSTER_Status 0x400 (100 ms), CLUSTER_Warning 0x401 (event + 500 ms). |
| RX (routed) | 0x100, 0x200, 0x201, 0x300, 0x301, 0x302, 0x500. |
| Error behaviour | Timeout of any monitored message -> `Warn_CommLoss`; invalid speed -> shows `DisplayedSpeed=255` (dashes); BMS fault -> `Warn_Battery`; `BrakeSystemFault` -> `Warn_Brake`. |
| Diagnostics | DTC U1100/U1101/U1103 (lost GATEWAY_ECU), E2E DTCs, own session handling. |

## GATEWAY_ECU (PT_CAN + INFO_CAN) - 0x704 / 0x70C
| Purpose | Routing allow-list, filtering, diagnostic routing, health/bus-load reporting. |
| TX | GW_Status 0x500 (100 ms, INFO_CAN), routed frames. |
| RX | All traffic on both buses. |
| Error behaviour | Unknown/disallowed ID -> dropped and `GW_RoutingErrorCount++` (saturates at 254); latency > 5 ms -> `GW_State=DEGRADED`. Never modifies payload. |
| Diagnostics | DTC U1112 (unexpected ID), U1100-U1102 (observed timeouts), DID F186/F189. |

## DIAG_TESTER (INFO_CAN)
| Purpose | Client for UDS-subset/OBD-II-inspired requests; timeout evaluation (P2 50 ms, S3 5 s); test oracle. |
| TX | 0x700-0x705. RX: 0x709-0x70D (+ status messages for observation). |
