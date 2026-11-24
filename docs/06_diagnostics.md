# 06 - Diagnostic Specification (academic subset)

**This is NOT a full ISO 14229 (UDS) or ISO 15765 (ISO-TP) implementation, nor a certified OBD-II stack.**
It is an educational subset using project-specific CAN IDs. Real OBD-II uses 0x7DF/0x7E0-0x7E8; Project 2 may remap.

## Addressing and transport
| Item | Value |
|---|---|
| Functional request | 0x700 (answered by each ECU on its own physical response ID) |
| Physical request / response | PT 0x701/0x709, BRAKE 0x702/0x70A, BMS 0x703/0x70B, GW 0x704/0x70C, CLUSTER 0x705/0x70D |
| Frame | Single frame: byte0 = PCI (0x0N, N = payload length <= 7), byte1 = SID, bytes 2-7 data, unused bytes 0x00 |
| Timing | P2 server 50 ms; S3 server 5 s (default session after expiry) |

## Implemented services (subset)
| SID | Service | Sub-function/params | Session | Positive response |
|---|---|---|---|---|
| 0x10 | DiagnosticSessionControl | 01 default, 03 extended | any | 50 sub P2(2B) P2*(2B) -> simplified to `50 sub` |
| 0x3E | TesterPresent | 00 | any | 7E 00 |
| 0x22 | ReadDataByIdentifier | DID F186 (active session, 1 B), F189 (SW version, 2 B major.minor), F18C (simulated serial number, 4 B) | any | 62 DID_hi DID_lo data |
| 0x19 | ReadDTCInformation | 01 (count by status mask), 02 (first DTC matching mask) | any | 59 01 mask fmt count_hi count_lo / 59 02 mask DTC(3B) status |
| 0x14 | ClearDiagnosticInformation | FFFFFF (all groups) | extended | 54 |
| OBD 0x01 | Show current data (inspired) | PID 0x00 (supported PIDs), 0x0D (vehicle speed, km/h = 1 byte) | any, functional or physical to BRAKE_ECU | 41 PID value |
Limitation: single-frame transport means 0x19 02 returns at most one DTC per request (project-specific restriction; multi-DTC via ISO-TP is future work).

## Negative responses `7F SID NRC`
| NRC | Meaning | Used when |
|---|---|---|
| 0x11 | serviceNotSupported | SID not in table |
| 0x12 | subFunctionNotSupported | unknown sub-function |
| 0x13 | incorrectMessageLengthOrInvalidFormat | PCI length wrong for the service |
| 0x22 | conditionsNotCorrect | e.g. clear while DTC source active (optional) |
| 0x31 | requestOutOfRange | unknown DID/PID |
| 0x7E | subFunctionNotSupportedInActiveSession | 0x14 sent in default session |
| 0x7F | serviceNotSupportedInActiveSession | service restricted to extended session |
Functional requests with unsupported service/sub-function are not answered (suppress NRC 0x11/0x12), following common practice.

## DTC format and catalogue (project-specific, manufacturer-range style codes)
DTC = 2 bytes code + 1 failure-type byte; status byte: bit0 testFailed, bit3 confirmedDTC (others unused).
Failure-type values below follow the commonly used UDS convention (0x87 missing message, 0x86 signal invalid, 0x82 alive-counter, 0x83 protection-calculation) - verify against your licensed ISO 14229-1 copy before citing.
| DTC | Meaning | Failure type | Detector(s) |
|---|---|---|---|
| U1100 | Lost communication with BRAKE_ECU (0x200/0x201 timeout) | 0x87 | PT, GW, CLUSTER |
| U1101 | Lost communication with BMS_ECU (0x300/0x301/0x302 timeout) | 0x87 | PT, GW, CLUSTER |
| U1102 | Lost communication with POWERTRAIN_ECU (0x100/0x101 timeout) | 0x87 | BRAKE, BMS, GW, CLUSTER |
| U1103 | Lost communication with GATEWAY_ECU (0x500 timeout) | 0x87 | CLUSTER |
| U1110 | E2E alive-counter error | 0x82 | any receiver |
| U1111 | E2E checksum error | 0x83 | any receiver |
| U1112 | Unexpected CAN ID observed | 0x00 | GW |
| C1201 | VehicleSpeed invalid / out of range | 0x86 | PT, CLUSTER, BRAKE |
| P1301 | BatteryVoltage invalid / out of range | 0x86 | PT, BMS |
| P1302 | BatteryTemperature invalid / out of range | 0x86 | PT, BMS |
| P1303 | BatteryCurrent invalid / out of range | 0x86 | PT, BMS |
Lifecycle: testFailed set at first failure; confirmed after debounce (3 failures); testFailed cleared after 5 good samples while confirmedDTC stays until 0x14.
Storage is volatile in simulation (no NVM) - documented limitation.

## Example sequences 
1. Session: `0x701: 02 10 03` -> `0x709: 02 50 03`
2. ReadDID serial: `0x703: 03 22 F1 8C` -> `0x70B: 07 62 F1 8C s1 s2 s3 s4` (a real VIN is 17 bytes and needs ISO-TP: future work, hence no F190 in v1.0)
3. DTC after fault F02: `0x701: 03 19 02 08` -> `0x709: 07 59 02 09 D1 00 87 09` (U1100 = bytes D1 00, failure type 87, status 0x09 = testFailed + confirmed)
4. OBD-inspired speed: `0x702: 02 01 0D` -> `0x70A: 03 41 0D vv`
5. Negative: `0x701: 02 2F 01` -> `0x709: 03 7F 2F 11`
