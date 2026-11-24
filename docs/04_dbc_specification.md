# 04 - DBC Specification and Compatibility Policy

File: `can_database/vehicle_v1_0.dbc` (v1.0.0), **generated** from `scripts/can_matrix.py` by `scripts/generate_dbc.py`.

## Conventions
- Messages `<DOMAIN>_<Name>` (PT_, BRAKE_, BMS_, CLUSTER_, GW_, DIAG_); signals CamelCase, with domain prefix where ambiguity is possible; frozen key names: `VehicleSpeed`, `BrakeStatus`, `SOC`, `SOH`, `BatteryVoltage`, `BatteryCurrent`, `BatteryTemperature`, `BMS_Fault`.
- Counter/CRC signals: `<MessageName>_Counter`, `<MessageName>_Checksum`.
- Intel byte order (`@1`), signed signals `@1-`.
- Sign convention: positive `BatteryCurrent` = discharge; positive `MotorTorque` = traction.
- Custom attributes: `GenMsgCycleTime`, `GenMsgSendType`, `MsgTimeoutMs`, `E2EProtected`, `OriginBus`, signal `SigInvalidRaw`, plus `DBVersion`.
- Value tables (`VAL_`) for all enumerations.

## Compatibility policy (semantic versioning)
| Change | Version | Allowed? |
|---|---|---|
| Add message in a reserved/owned range, add signal in reserved bits | minor (1.1.0) | yes |
| Add enum value | minor | yes |
| Rename/renumber message, move/resize/rescale a released signal, change cycle time class | major (2.0.0) | only with migration note in doc 12 |
| Documentation/comment fix | patch | yes |

## Verification performed (executed)
`tests/unit/test_dbc_static.py` (TC-001..TC-008): strict load, unique standard IDs and range ownership, min/max encode-decode round-trip for every signal, E2E layout in all 10 protected messages, generator drift, invalid-value placement.
Not verified: import into CANoe/CANalyzer (requires those tools).
