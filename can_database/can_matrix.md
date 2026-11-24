# CAN matrix v1.0.0 (GENERATED -  scripts/can_matrix.py)

Both networks: 500 kbit/s, 11-bit identifiers, DLC 8, Intel byte order.

## Messages

| ID | Name | Sender | Receivers | Origin bus | Type | Cycle ms | Timeout ms | E2E |
|---|---|---|---|---|---|---|---|---|
| 0x100 | PT_Status | POWERTRAIN_ECU | BRAKE_ECU, BMS_ECU, GATEWAY_ECU, CLUSTER_ECU | PT_CAN | Cyclic | 20 | 60 | yes |
| 0x101 | PT_Torque | POWERTRAIN_ECU | BMS_ECU, GATEWAY_ECU | PT_CAN | Cyclic | 10 | 30 | yes |
| 0x200 | BRAKE_Status | BRAKE_ECU | POWERTRAIN_ECU, GATEWAY_ECU, CLUSTER_ECU | PT_CAN | Cyclic | 20 | 60 | yes |
| 0x201 | BRAKE_VehicleDynamics | BRAKE_ECU | POWERTRAIN_ECU, GATEWAY_ECU, CLUSTER_ECU | PT_CAN | Cyclic | 10 | 30 | yes |
| 0x300 | BMS_Status | BMS_ECU | POWERTRAIN_ECU, GATEWAY_ECU, CLUSTER_ECU | PT_CAN | Cyclic | 100 | 300 | yes |
| 0x301 | BMS_Measurements | BMS_ECU | POWERTRAIN_ECU, GATEWAY_ECU, CLUSTER_ECU | PT_CAN | Cyclic | 50 | 150 | yes |
| 0x302 | BMS_Faults | BMS_ECU | POWERTRAIN_ECU, GATEWAY_ECU, CLUSTER_ECU | PT_CAN | CyclicAndEvent | 500 | 1500 | yes |
| 0x400 | CLUSTER_Status | CLUSTER_ECU | GATEWAY_ECU, DIAG_TESTER | INFO_CAN | Cyclic | 100 | 300 | yes |
| 0x401 | CLUSTER_Warning | CLUSTER_ECU | GATEWAY_ECU, DIAG_TESTER | INFO_CAN | CyclicAndEvent | 500 | 1500 | yes |
| 0x500 | GW_Status | GATEWAY_ECU | CLUSTER_ECU, DIAG_TESTER | INFO_CAN | Cyclic | 100 | 300 | yes |
| 0x700 | DIAG_REQ_FUNC | DIAG_TESTER | POWERTRAIN_ECU, BRAKE_ECU, BMS_ECU, GATEWAY_ECU, CLUSTER_ECU | INFO_CAN | Event | - | - | no |
| 0x701 | DIAG_REQ_PT | DIAG_TESTER | POWERTRAIN_ECU, GATEWAY_ECU | INFO_CAN | Event | - | - | no |
| 0x702 | DIAG_REQ_BRAKE | DIAG_TESTER | BRAKE_ECU, GATEWAY_ECU | INFO_CAN | Event | - | - | no |
| 0x703 | DIAG_REQ_BMS | DIAG_TESTER | BMS_ECU, GATEWAY_ECU | INFO_CAN | Event | - | - | no |
| 0x704 | DIAG_REQ_GW | DIAG_TESTER | GATEWAY_ECU | INFO_CAN | Event | - | - | no |
| 0x705 | DIAG_REQ_CLUSTER | DIAG_TESTER | CLUSTER_ECU | INFO_CAN | Event | - | - | no |
| 0x709 | DIAG_RESP_PT | POWERTRAIN_ECU | DIAG_TESTER, GATEWAY_ECU | PT_CAN | Event | - | - | no |
| 0x70A | DIAG_RESP_BRAKE | BRAKE_ECU | DIAG_TESTER, GATEWAY_ECU | PT_CAN | Event | - | - | no |
| 0x70B | DIAG_RESP_BMS | BMS_ECU | DIAG_TESTER, GATEWAY_ECU | PT_CAN | Event | - | - | no |
| 0x70C | DIAG_RESP_GW | GATEWAY_ECU | DIAG_TESTER | INFO_CAN | Event | - | - | no |
| 0x70D | DIAG_RESP_CLUSTER | CLUSTER_ECU | DIAG_TESTER | INFO_CAN | Event | - | - | no |

## Signals (application messages)

| Message | Signal | Start|Len | Signed | Factor | Offset | Range | Unit | Invalid raw | Values |
|---|---|---|---|---|---|---|---|---|---|
| PT_Status | PT_State | 0|4 | N | 1 | 0 | 0..5 |  | 15 | 0=OFF, 1=INIT, 2=READY, 3=DRIVE, 4=DEGRADED, 5=FAULT, 15=INVALID |
| PT_Status | PT_GearPosition | 4|4 | N | 1 | 0 | 0..3 |  | 15 | 0=PARK, 1=REVERSE, 2=NEUTRAL, 3=DRIVE, 15=INVALID |
| PT_Status | PT_DriveMode | 8|2 | N | 1 | 0 | 0..2 |  | 3 | 0=ECO, 1=NORMAL, 2=SPORT, 3=INVALID |
| PT_Status | PT_ReadyToDrive | 10|1 | N | 1 | 0 | 0..1 |  |  | 0=FALSE, 1=TRUE |
| PT_Status | PT_FaultActive | 11|1 | N | 1 | 0 | 0..1 |  |  | 0=FALSE, 1=TRUE |
| PT_Status | PT_Status_Counter | 48|4 | N | 1 | 0 | 0..15 |  |  |  |
| PT_Status | PT_Status_Checksum | 56|8 | N | 1 | 0 | 0..255 |  |  |  |
| PT_Torque | MotorTorqueRequest | 0|16 | Y | 0.1 | 0 | -400..400 | Nm | 32767 |  |
| PT_Torque | MotorTorqueActual | 16|16 | Y | 0.1 | 0 | -400..400 | Nm | 32767 |  |
| PT_Torque | MotorSpeed | 32|16 | Y | 1 | 0 | -500..12000 | rpm | 32767 |  |
| PT_Torque | PT_Torque_Counter | 48|4 | N | 1 | 0 | 0..15 |  |  |  |
| PT_Torque | PT_Torque_Checksum | 56|8 | N | 1 | 0 | 0..255 |  |  |  |
| BRAKE_Status | BrakeStatus | 0|2 | N | 1 | 0 | 0..2 |  | 3 | 0=RELEASED, 1=APPLIED, 2=FAULT, 3=INVALID |
| BRAKE_Status | ABS_Active | 2|1 | N | 1 | 0 | 0..1 |  |  | 0=FALSE, 1=TRUE |
| BRAKE_Status | BrakeSystemFault | 3|1 | N | 1 | 0 | 0..1 |  |  | 0=FALSE, 1=TRUE |
| BRAKE_Status | BrakePedalPosition | 8|8 | N | 0.5 | 0 | 0..100 | % | 255 |  |
| BRAKE_Status | BrakePressure | 16|12 | N | 0.1 | 0 | 0..250 | bar | 4095 |  |
| BRAKE_Status | BRAKE_Status_Counter | 48|4 | N | 1 | 0 | 0..15 |  |  |  |
| BRAKE_Status | BRAKE_Status_Checksum | 56|8 | N | 1 | 0 | 0..255 |  |  |  |
| BRAKE_VehicleDynamics | VehicleSpeed | 0|16 | N | 0.01 | 0 | 0..300 | km/h | 65535 |  |
| BRAKE_VehicleDynamics | LongitudinalAccel | 16|16 | Y | 0.001 | 0 | -20..20 | m/s2 | 32767 |  |
| BRAKE_VehicleDynamics | YawRate | 32|16 | Y | 0.01 | 0 | -300..300 | deg/s | 32767 |  |
| BRAKE_VehicleDynamics | BRAKE_VehicleDynamics_Counter | 48|4 | N | 1 | 0 | 0..15 |  |  |  |
| BRAKE_VehicleDynamics | BRAKE_VehicleDynamics_Checksum | 56|8 | N | 1 | 0 | 0..255 |  |  |  |
| BMS_Status | BMS_State | 0|4 | N | 1 | 0 | 0..5 |  | 15 | 0=OFF, 1=INIT, 2=STANDBY, 3=CHARGING, 4=DISCHARGING, 5=FAULT, 15=INVALID |
| BMS_Status | ContactorState | 4|2 | N | 1 | 0 | 0..2 |  | 3 | 0=OPEN, 1=CLOSED, 2=PRECHARGE, 3=INVALID |
| BMS_Status | SOC | 8|10 | N | 0.1 | 0 | 0..100 | % | 1023 |  |
| BMS_Status | SOH | 18|10 | N | 0.1 | 0 | 0..100 | % | 1023 |  |
| BMS_Status | BMS_Status_Counter | 48|4 | N | 1 | 0 | 0..15 |  |  |  |
| BMS_Status | BMS_Status_Checksum | 56|8 | N | 1 | 0 | 0..255 |  |  |  |
| BMS_Measurements | BatteryVoltage | 0|16 | N | 0.1 | 0 | 0..500 | V | 65535 |  |
| BMS_Measurements | BatteryCurrent | 16|16 | Y | 0.1 | 0 | -500..500 | A | 32767 |  |
| BMS_Measurements | BatteryTemperature | 32|8 | N | 1 | -40 | -40..125 | degC | 255 |  |
| BMS_Measurements | BMS_Measurements_Counter | 48|4 | N | 1 | 0 | 0..15 |  |  |  |
| BMS_Measurements | BMS_Measurements_Checksum | 56|8 | N | 1 | 0 | 0..255 |  |  |  |
| BMS_Faults | BMS_Fault | 0|8 | N | 1 | 0 | 0..6 |  | 255 | 0=NONE, 1=OVERVOLTAGE, 2=UNDERVOLTAGE, 3=OVERTEMPERATURE, 4=OVERCURRENT, 5=COMM_LOSS, 6=SENSOR_INVALID, 255=INVALID |
| BMS_Faults | BMS_FaultSeverity | 8|2 | N | 1 | 0 | 0..3 |  |  | 0=NONE, 1=WARNING, 2=ERROR, 3=CRITICAL |
| BMS_Faults | BMS_FaultActive | 10|1 | N | 1 | 0 | 0..1 |  |  | 0=FALSE, 1=TRUE |
| BMS_Faults | BMS_Faults_Counter | 48|4 | N | 1 | 0 | 0..15 |  |  |  |
| BMS_Faults | BMS_Faults_Checksum | 56|8 | N | 1 | 0 | 0..255 |  |  |  |
| CLUSTER_Status | Cluster_State | 0|4 | N | 1 | 0 | 0..3 |  | 15 | 0=OFF, 1=INIT, 2=ACTIVE, 3=DEGRADED, 15=INVALID |
| CLUSTER_Status | DisplayedSpeed | 8|8 | N | 1 | 0 | 0..250 | km/h | 255 |  |
| CLUSTER_Status | DisplayedSOC | 16|8 | N | 0.4 | 0 | 0..100 | % | 255 |  |
| CLUSTER_Status | CLUSTER_Status_Counter | 48|4 | N | 1 | 0 | 0..15 |  |  |  |
| CLUSTER_Status | CLUSTER_Status_Checksum | 56|8 | N | 1 | 0 | 0..255 |  |  |  |
| CLUSTER_Warning | Warn_Battery | 0|1 | N | 1 | 0 | 0..1 |  |  | 0=FALSE, 1=TRUE |
| CLUSTER_Warning | Warn_Brake | 1|1 | N | 1 | 0 | 0..1 |  |  | 0=FALSE, 1=TRUE |
| CLUSTER_Warning | Warn_Powertrain | 2|1 | N | 1 | 0 | 0..1 |  |  | 0=FALSE, 1=TRUE |
| CLUSTER_Warning | Warn_CommLoss | 3|1 | N | 1 | 0 | 0..1 |  |  | 0=FALSE, 1=TRUE |
| CLUSTER_Warning | Warn_Diagnostic | 4|1 | N | 1 | 0 | 0..1 |  |  | 0=FALSE, 1=TRUE |
| CLUSTER_Warning | Warn_Gateway | 5|1 | N | 1 | 0 | 0..1 |  |  | 0=FALSE, 1=TRUE |
| CLUSTER_Warning | CLUSTER_Warning_Counter | 48|4 | N | 1 | 0 | 0..15 |  |  |  |
| CLUSTER_Warning | CLUSTER_Warning_Checksum | 56|8 | N | 1 | 0 | 0..255 |  |  |  |
| GW_Status | GW_State | 0|4 | N | 1 | 0 | 0..4 |  | 15 | 0=OFF, 1=INIT, 2=NORMAL, 3=DEGRADED, 4=FAULT, 15=INVALID |
| GW_Status | GW_BusLoadPT | 8|8 | N | 0.5 | 0 | 0..100 | % | 255 |  |
| GW_Status | GW_BusLoadINFO | 16|8 | N | 0.5 | 0 | 0..100 | % | 255 |  |
| GW_Status | GW_RoutingErrorCount | 24|8 | N | 1 | 0 | 0..254 |  | 255 |  |
| GW_Status | GW_Status_Counter | 48|4 | N | 1 | 0 | 0..15 |  |  |  |
| GW_Status | GW_Status_Checksum | 56|8 | N | 1 | 0 | 0..255 |  |  |  |

## Diagnostic messages

Raw single-frame payload: `PCI(0|8) SID(8|8) Data(16|48)`. Response ID = request ID + 0x08 (0x708 reserved: no functional response).

## Gateway routing allow-list (default deny)

| CAN ID | Name | From | To |
|---|---|---|---|
| 0x100 | PT_Status | PT_CAN | INFO_CAN |
| 0x200 | BRAKE_Status | PT_CAN | INFO_CAN |
| 0x201 | BRAKE_VehicleDynamics | PT_CAN | INFO_CAN |
| 0x300 | BMS_Status | PT_CAN | INFO_CAN |
| 0x301 | BMS_Measurements | PT_CAN | INFO_CAN |
| 0x302 | BMS_Faults | PT_CAN | INFO_CAN |
| 0x709 | DIAG_RESP_PT | PT_CAN | INFO_CAN |
| 0x70A | DIAG_RESP_BRAKE | PT_CAN | INFO_CAN |
| 0x70B | DIAG_RESP_BMS | PT_CAN | INFO_CAN |
| 0x700 | DIAG_REQ_FUNC | INFO_CAN | PT_CAN |
| 0x701 | DIAG_REQ_PT | INFO_CAN | PT_CAN |
| 0x702 | DIAG_REQ_BRAKE | INFO_CAN | PT_CAN |
| 0x703 | DIAG_REQ_BMS | INFO_CAN | PT_CAN |

## Theoretical bus load (ANALYTICAL - not measured)

Nominal periodic traffic only (event bursts and diagnostics excluded), 8-byte standard frames: 111 bit/frame without stuffing, 135 bit/frame worst-case stuffing.

| Bus | Frames/s | Load, no stuffing | Load, worst-case stuffing |
|---|---|---|---|
| PT_CAN | 332 | 7.4 % | 9.0 % |
| INFO_CAN | 254 | 5.6 % | 6.9 % |
