"""Single source of truth for the vehicle CAN matrix (v1.0.0).

DBC, CSV and Markdown tables are GENERATED from this file by generate_dbc.py.
Compatibility policy (see docs/04_dbc_specification.md): additive changes only;
never renumber IDs, rename signals/ECUs, or move start bits of released signals.
"""
VERSION = "1.0.0"
BITRATE = 500_000
PT, BR, BMS, CL, GW, DT = ("POWERTRAIN_ECU", "BRAKE_ECU", "BMS_ECU",
                           "CLUSTER_ECU", "GATEWAY_ECU", "DIAG_TESTER")
NODES = [PT, BR, BMS, CL, GW, DT]
BUSES = {"PT_CAN": [PT, BR, BMS, GW], "INFO_CAN": [GW, CL, DT]}


def sig(name, start, length, factor=1, offset=0, lo=0, hi=None, unit="",
        invalid=None, signed=False, enum=None, comment=""):
    return dict(name=name, start=start, length=length, factor=factor, offset=offset,
                lo=lo, hi=hi, unit=unit, invalid=invalid, signed=signed,
                enum=enum, comment=comment)


def msg(mid, name, sender, rx, cycle, send_type, signals, bus, protected=True,
        comment=""):
    timeout = cycle * 3 if cycle else None
    return dict(id=mid, name=name, dlc=8, sender=sender, receivers=rx, cycle=cycle,
                send_type=send_type, timeout=timeout, signals=signals, bus=bus,
                protected=protected, comment=comment)


E_PT = {0: "OFF", 1: "INIT", 2: "READY", 3: "DRIVE", 4: "DEGRADED", 5: "FAULT", 15: "INVALID"}
E_GEAR = {0: "PARK", 1: "REVERSE", 2: "NEUTRAL", 3: "DRIVE", 15: "INVALID"}
E_MODE = {0: "ECO", 1: "NORMAL", 2: "SPORT", 3: "INVALID"}
E_BRK = {0: "RELEASED", 1: "APPLIED", 2: "FAULT", 3: "INVALID"}
E_BMS = {0: "OFF", 1: "INIT", 2: "STANDBY", 3: "CHARGING", 4: "DISCHARGING", 5: "FAULT", 15: "INVALID"}
E_CONT = {0: "OPEN", 1: "CLOSED", 2: "PRECHARGE", 3: "INVALID"}
E_BFLT = {0: "NONE", 1: "OVERVOLTAGE", 2: "UNDERVOLTAGE", 3: "OVERTEMPERATURE",
          4: "OVERCURRENT", 5: "COMM_LOSS", 6: "SENSOR_INVALID", 255: "INVALID"}
E_SEV = {0: "NONE", 1: "WARNING", 2: "ERROR", 3: "CRITICAL"}
E_CL = {0: "OFF", 1: "INIT", 2: "ACTIVE", 3: "DEGRADED", 15: "INVALID"}
E_GW = {0: "OFF", 1: "INIT", 2: "NORMAL", 3: "DEGRADED", 4: "FAULT", 15: "INVALID"}
E_B = {0: "FALSE", 1: "TRUE"}

MESSAGES = [
    msg(0x100, "PT_Status", PT, [BR, BMS, GW, CL], 20, "Cyclic", [
        sig("PT_State", 0, 4, hi=5, invalid=15, enum=E_PT),
        sig("PT_GearPosition", 4, 4, hi=3, invalid=15, enum=E_GEAR),
        sig("PT_DriveMode", 8, 2, hi=2, invalid=3, enum=E_MODE),
        sig("PT_ReadyToDrive", 10, 1, hi=1, enum=E_B),
        sig("PT_FaultActive", 11, 1, hi=1, enum=E_B)], "PT_CAN",
        comment="Powertrain state, gear, drive mode"),
    msg(0x101, "PT_Torque", PT, [BMS, GW], 10, "Cyclic", [
        sig("MotorTorqueRequest", 0, 16, 0.1, 0, -400, 400, "Nm", 32767, True),
        sig("MotorTorqueActual", 16, 16, 0.1, 0, -400, 400, "Nm", 32767, True),
        sig("MotorSpeed", 32, 16, 1, 0, -500, 12000, "rpm", 32767, True)], "PT_CAN",
        comment="Motor torque and speed (not routed to INFO_CAN: demonstrates filtering)"),
    msg(0x200, "BRAKE_Status", BR, [PT, GW, CL], 20, "Cyclic", [
        sig("BrakeStatus", 0, 2, hi=2, invalid=3, enum=E_BRK),
        sig("ABS_Active", 2, 1, hi=1, enum=E_B),
        sig("BrakeSystemFault", 3, 1, hi=1, enum=E_B),
        sig("BrakePedalPosition", 8, 8, 0.5, 0, 0, 100, "%", 255),
        sig("BrakePressure", 16, 12, 0.1, 0, 0, 250, "bar", 4095)], "PT_CAN",
        comment="Brake system status"),
    msg(0x201, "BRAKE_VehicleDynamics", BR, [PT, GW, CL], 10, "Cyclic", [
        sig("VehicleSpeed", 0, 16, 0.01, 0, 0, 300, "km/h", 65535),
        sig("LongitudinalAccel", 16, 16, 0.001, 0, -20, 20, "m/s2", 32767, True),
        sig("YawRate", 32, 16, 0.01, 0, -300, 300, "deg/s", 32767, True)], "PT_CAN",
        comment="Wheel-speed-derived vehicle dynamics (reused by Project 3 AEB)"),
    msg(0x300, "BMS_Status", BMS, [PT, GW, CL], 100, "Cyclic", [
        sig("BMS_State", 0, 4, hi=5, invalid=15, enum=E_BMS),
        sig("ContactorState", 4, 2, hi=2, invalid=3, enum=E_CONT),
        sig("SOC", 8, 10, 0.1, 0, 0, 100, "%", 1023),
        sig("SOH", 18, 10, 0.1, 0, 0, 100, "%", 1023)], "PT_CAN",
        comment="Battery state, SOC, SOH"),
    msg(0x301, "BMS_Measurements", BMS, [PT, GW, CL], 50, "Cyclic", [
        sig("BatteryVoltage", 0, 16, 0.1, 0, 0, 500, "V", 65535),
        sig("BatteryCurrent", 16, 16, 0.1, 0, -500, 500, "A", 32767, True),
        sig("BatteryTemperature", 32, 8, 1, -40, -40, 125, "degC", 255)], "PT_CAN",
        comment="Pack measurements. Positive current = discharge (convention frozen)"),
    msg(0x302, "BMS_Faults", BMS, [PT, GW, CL], 500, "CyclicAndEvent", [
        sig("BMS_Fault", 0, 8, hi=6, invalid=255, enum=E_BFLT),
        sig("BMS_FaultSeverity", 8, 2, hi=3, enum=E_SEV),
        sig("BMS_FaultActive", 10, 1, hi=1, enum=E_B)], "PT_CAN",
        comment="Event-triggered on change (<=10 ms), 500 ms heartbeat"),
    msg(0x400, "CLUSTER_Status", CL, [GW, DT], 100, "Cyclic", [
        sig("Cluster_State", 0, 4, hi=3, invalid=15, enum=E_CL),
        sig("DisplayedSpeed", 8, 8, 1, 0, 0, 250, "km/h", 255),
        sig("DisplayedSOC", 16, 8, 0.4, 0, 0, 100, "%", 255)], "INFO_CAN",
        comment="What the cluster currently displays"),
    msg(0x401, "CLUSTER_Warning", CL, [GW, DT], 500, "CyclicAndEvent", [
        sig("Warn_Battery", 0, 1, hi=1, enum=E_B),
        sig("Warn_Brake", 1, 1, hi=1, enum=E_B),
        sig("Warn_Powertrain", 2, 1, hi=1, enum=E_B),
        sig("Warn_CommLoss", 3, 1, hi=1, enum=E_B),
        sig("Warn_Diagnostic", 4, 1, hi=1, enum=E_B),
        sig("Warn_Gateway", 5, 1, hi=1, enum=E_B)], "INFO_CAN",
        comment="Warning lamps; event on change, 500 ms heartbeat"),
    msg(0x500, "GW_Status", GW, [CL, DT], 100, "Cyclic", [
        sig("GW_State", 0, 4, hi=4, invalid=15, enum=E_GW),
        sig("GW_BusLoadPT", 8, 8, 0.5, 0, 0, 100, "%", 255),
        sig("GW_BusLoadINFO", 16, 8, 0.5, 0, 0, 100, "%", 255),
        sig("GW_RoutingErrorCount", 24, 8, 1, 0, 0, 254, "", 255)], "INFO_CAN",
        comment="Gateway health and measured bus load"),
]

# Diagnostics: single-frame transport only in v1.0. Response ID = request ID + 0x08.
_DIAG = [
    (0x700, "DIAG_REQ_FUNC", DT, [PT, BR, BMS, GW, CL], "INFO_CAN", "Functional request (broadcast)"),
    (0x701, "DIAG_REQ_PT", DT, [PT, GW], "INFO_CAN", "Physical request to POWERTRAIN_ECU"),
    (0x702, "DIAG_REQ_BRAKE", DT, [BR, GW], "INFO_CAN", "Physical request to BRAKE_ECU"),
    (0x703, "DIAG_REQ_BMS", DT, [BMS, GW], "INFO_CAN", "Physical request to BMS_ECU"),
    (0x704, "DIAG_REQ_GW", DT, [GW], "INFO_CAN", "Physical request to GATEWAY_ECU"),
    (0x705, "DIAG_REQ_CLUSTER", DT, [CL], "INFO_CAN", "Physical request to CLUSTER_ECU"),
    (0x709, "DIAG_RESP_PT", PT, [DT, GW], "PT_CAN", "Response of POWERTRAIN_ECU"),
    (0x70A, "DIAG_RESP_BRAKE", BR, [DT, GW], "PT_CAN", "Response of BRAKE_ECU"),
    (0x70B, "DIAG_RESP_BMS", BMS, [DT, GW], "PT_CAN", "Response of BMS_ECU"),
    (0x70C, "DIAG_RESP_GW", GW, [DT], "INFO_CAN", "Response of GATEWAY_ECU"),
    (0x70D, "DIAG_RESP_CLUSTER", CL, [DT], "INFO_CAN", "Response of CLUSTER_ECU"),
]
for _id, _n, _s, _rx, _bus, _c in _DIAG:
    MESSAGES.append(msg(_id, _n, _s, _rx, None, "Event", [
        sig(f"{_n}_PCI", 0, 8, hi=255),
        sig(f"{_n}_SID", 8, 8, hi=255),
        sig(f"{_n}_Data", 16, 48, hi=2**48 - 1)], _bus, protected=False, comment=_c))

# Gateway routing: default-deny allow-list. (can_id, from_bus, to_bus)
ROUTES = [(i, "PT_CAN", "INFO_CAN") for i in (0x100, 0x200, 0x201, 0x300, 0x301, 0x302, 0x709, 0x70A, 0x70B)] + \
         [(i, "INFO_CAN", "PT_CAN") for i in (0x700, 0x701, 0x702, 0x703)]
# Intentionally blocked (documented, tested): 0x101 PT->INFO; 0x400/0x401/0x500 INFO->PT.
