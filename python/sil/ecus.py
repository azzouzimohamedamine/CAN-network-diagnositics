"""Python ports of capl/{brake,bms,cluster,powertrain}_ecu.can. Same logic, constants and plant placeholders.
Plant models (speed, battery) are simulated placeholders, not validated models."""
from .kernel import Ecu
from . import supervision as S


class BrakeEcu(Ecu):
    NAME = "BRAKE_ECU"

    def __init__(self, sim):
        super().__init__(sim)
        self.sup.add("PT_Status", self.codec.timeout("PT_Status"), S.DTC_U1102)
        self.handlers = {"PT_Status": lambda r: None}
        self.speed_ms = self.pedal = self.accel = 0.0

    def press(self, key):
        if key == "w" and self.speed_ms < 80.0:
            self.speed_ms += 1.0
        elif key == "q":
            self.speed_ms = max(0.0, self.speed_ms - 1.0)
        elif key == "b":
            self.pedal = 0.0 if self.pedal > 0.0 else 60.0

    def step(self, t):
        if self.every("status", 20, t):
            self.send("BRAKE_Status", phys=dict(BrakeStatus=1 if self.pedal >= 2.0 else 0, ABS_Active=0,
                      BrakeSystemFault=0, BrakePedalPosition=self.pedal, BrakePressure=self.pedal * 1.5))
        if self.every("dyn", 10, t):
            self.sup.tick()
            self.accel = -self.pedal * 0.1 if self.pedal > 0.0 else 0.0
            self.speed_ms += self.accel * 0.01
            if self.speed_ms < 0.0:
                self.speed_ms, self.accel = 0.0, 0.0
            self.send("BRAKE_VehicleDynamics", phys=dict(VehicleSpeed=self.speed_ms * 3.6,
                      LongitudinalAccel=self.accel, YawRate=0.0))


class BmsEcu(Ecu):
    NAME = "BMS_ECU"
    SIM_ACCEL = 20.0

    def __init__(self, sim):
        super().__init__(sim)
        self.sup.add("PT_Torque", self.codec.timeout("PT_Torque"), S.DTC_U1102)
        self.handlers = {"PT_Torque": self._on_torque}
        self.soc, self.soh, self.volt, self.cur, self.temp = 80.0, 95.0, 380.0, 0.0, 25.0
        self.torque = self.rpm = 0.0
        self.init_done, self.contactor, self.fault, self.sev = False, 0, 0, 0

    def _on_torque(self, r):
        self.torque = self.codec.phys("PT_Torque", "MotorTorqueActual", r["MotorTorqueActual"])
        self.rpm = self.codec.phys("PT_Torque", "MotorSpeed", r["MotorSpeed"])

    def _send_fault(self, t):
        self.send("BMS_Faults", phys=dict(BMS_Fault=self.fault, BMS_FaultSeverity=self.sev,
                  BMS_FaultActive=1 if self.fault else 0))
        self.due["hb"] = t + 500

    def step(self, t):
        if not self.init_done and t >= 500:
            self.init_done, self.contactor = True, 1
        if self.every("tick", 10, t):
            self.sup.tick()
            dt = 0.01 * self.SIM_ACCEL
            if not self.sup.ok("PT_Torque"):
                self.torque = self.rpm = 0.0
            power = 0.0 if self.contactor == 0 else self.torque * self.rpm * 0.10472
            self.cur = power / self.volt / 0.92 if power >= 0.0 else power / self.volt * 0.92
            self.soc = min(100.0, max(0.0, self.soc - self.cur * dt / (60.0 * 3600.0) * 100.0))
            self.volt = 300.0 + self.soc - self.cur * 0.05
            self.temp += (self.cur ** 2 * 0.05 / 20000.0) * dt - (self.temp - 25.0) / 200.0 * dt
            nf, ns = 0, 0
            if self.temp > 60.0:
                nf, ns = 3, 3 if self.temp > 65.0 else 2
            elif self.cur > 350.0:
                nf, ns = 4, 2
            elif self.volt < 310.0:
                nf, ns = 2, 2
            elif self.volt > 410.0:
                nf, ns = 1, 2
            elif not self.sup.ok("PT_Torque"):
                nf, ns = 5, 1
            if ns == 3:
                self.contactor = 0
            if (nf, ns) != (self.fault, self.sev):
                self.fault, self.sev = nf, ns
                self._send_fault(t)
        if t >= self.due.get("hb", 100):
            self._send_fault(t)
        if self.every("status", 100, t):
            st = 1 if not self.init_done else 5 if self.sev >= 2 else 4 if self.cur > 1.0 else 3 if self.cur < -1.0 else 2
            self.send("BMS_Status", phys=dict(BMS_State=st, ContactorState=self.contactor, SOC=self.soc, SOH=self.soh))
        if self.every("meas", 50, t):
            self.send("BMS_Measurements", phys=dict(BatteryVoltage=self.volt, BatteryCurrent=self.cur,
                                                    BatteryTemperature=self.temp))


class ClusterEcu(Ecu):
    NAME = "CLUSTER_ECU"
    MON = {"PT_Status": S.DTC_U1102, "BRAKE_Status": S.DTC_U1100, "BRAKE_VehicleDynamics": S.DTC_U1100,
           "BMS_Status": S.DTC_U1101, "BMS_Measurements": S.DTC_U1101, "BMS_Faults": S.DTC_U1101}

    def __init__(self, sim):
        super().__init__(sim)
        for n, d in self.MON.items():
            self.sup.add(n, self.codec.timeout(n), d)
        self.handlers = {"PT_Status": lambda r: setattr(self, "pt_fault", r["PT_FaultActive"]),
                         "BRAKE_Status": lambda r: setattr(self, "brake_fault", r["BrakeSystemFault"]),
                         "BRAKE_VehicleDynamics": self._on_dyn, "BMS_Status": self._on_bms,
                         "BMS_Measurements": lambda r: None,
                         "BMS_Faults": lambda r: setattr(self, "bms_fault", r["BMS_FaultActive"])}
        self.init_done = False
        self.speed_ok = self.soc_ok = False
        self.speed = self.soc = 0.0
        self.pt_fault = self.brake_fault = self.bms_fault = 0
        self.warn = (0, 0, 0, 0)       # battery, brake, powertrain, commloss

    def _on_dyn(self, r):
        self.speed_ok = self.sup.check_signal("speed", r["VehicleSpeed"], 65535, 0, 30000, S.DTC_C1201)
        if self.speed_ok:
            self.speed = self.codec.phys("BRAKE_VehicleDynamics", "VehicleSpeed", r["VehicleSpeed"])

    def _on_bms(self, r):
        self.soc_ok = r["SOC"] != 1023 and r["SOC"] <= 1000
        if self.soc_ok:
            self.soc = self.codec.phys("BMS_Status", "SOC", r["SOC"])

    def _send_warn(self, t):
        b, br, pt, c = self.warn
        self.send("CLUSTER_Warning", phys=dict(Warn_Battery=b, Warn_Brake=br, Warn_Powertrain=pt, Warn_CommLoss=c))
        self.due["hb"] = t + 500

    def step(self, t):
        if not self.init_done and t >= 500:
            self.init_done = True
        if self.every("tick", 10, t):
            self.sup.tick()
            ok = self.sup.ok
            comm = int(not all(ok(n) for n in self.MON))
            wb = int(bool(self.bms_fault) or not ok("BMS_Status") or not ok("BMS_Faults"))
            wbr = int(bool(self.brake_fault) or not ok("BRAKE_Status"))
            wpt = int(bool(self.pt_fault) or not ok("PT_Status"))
            if (wb, wbr, wpt, comm) != self.warn:
                self.warn = (wb, wbr, wpt, comm)
                self._send_warn(t)
        if t >= self.due.get("hb", 150):
            self._send_warn(t)
        if self.every("status", 100, t):
            state = 1 if not self.init_done else 3 if self.warn[3] else 2
            raw = {}
            phys = dict(Cluster_State=state)
            if self.speed_ok and self.sup.ok("BRAKE_VehicleDynamics"):
                phys["DisplayedSpeed"] = self.speed
            else:
                raw["DisplayedSpeed"] = 255
            if self.soc_ok and self.sup.ok("BMS_Status"):
                phys["DisplayedSOC"] = self.soc
            else:
                raw["DisplayedSOC"] = 255
            self.send("CLUSTER_Status", phys=phys, raw=raw)


class PowertrainEcu(Ecu):
    NAME = "POWERTRAIN_ECU"
    MON = {"BRAKE_Status": S.DTC_U1100, "BRAKE_VehicleDynamics": S.DTC_U1100, "BMS_Status": S.DTC_U1101,
           "BMS_Measurements": S.DTC_U1101, "BMS_Faults": S.DTC_U1101}

    def __init__(self, sim):
        super().__init__(sim)
        for n, d in self.MON.items():
            self.sup.add(n, self.codec.timeout(n), d)
        self.handlers = {"BRAKE_Status": self._on_brake, "BRAKE_VehicleDynamics": self._on_dyn,
                         "BMS_Status": lambda r: None, "BMS_Measurements": self._on_meas,
                         "BMS_Faults": self._on_faults}
        self.state, self.health, self.gear = 1, 0, 0       # base state 1 INIT / 2 READY / 3 DRIVE
        self.req = self.cmd = self.act = self.rpm = 0.0
        self.brake_applied = self.brake_fault = self.bms_fault = False
        self.bms_sev, self.speed_bad_ms, self.speed = 0, 0, 0.0

    def _on_brake(self, r):
        self.brake_applied = r["BrakeStatus"] == 1
        self.brake_fault = r["BrakeSystemFault"] != 0 or r["BrakeStatus"] == 2

    def _on_dyn(self, r):
        if self.sup.check_signal("speed", r["VehicleSpeed"], 65535, 0, 30000, S.DTC_C1201):
            self.speed = self.codec.phys("BRAKE_VehicleDynamics", "VehicleSpeed", r["VehicleSpeed"])
            self.speed_bad_ms = 0
        else:
            self.speed_bad_ms += 10

    def _on_meas(self, r):
        self.sup.check_signal("volt", r["BatteryVoltage"], 65535, 0, 5000, S.DTC_P1301)
        self.sup.check_signal("cur", r["BatteryCurrent"], 32767, -5000, 5000, S.DTC_P1303)
        self.sup.check_signal("temp", r["BatteryTemperature"], 255, 0, 165, S.DTC_P1302)

    def _on_faults(self, r):
        self.bms_fault, self.bms_sev = bool(r["BMS_FaultActive"]), r["BMS_FaultSeverity"]

    def press(self, key):
        if key == "s" and self.state == 2 and self.health == 0:
            self.gear, self.state = 3, 3
        elif key == "x":
            self.req, self.gear = 0.0, 0
            if self.state == 3:
                self.state = 2
        elif key == "u" and self.state == 3 and self.req < 400.0:
            self.req += 20.0
        elif key == "d" and self.state == 3 and self.req > -400.0:
            self.req -= 20.0
        elif key == "g":
            self.gear = (self.gear + 1) % 4

    def published_state(self):
        if self.state in (0, 1):
            return self.state
        if self.health == 2:
            return 5
        if self.health == 1 and self.state == 3:
            return 4
        return self.state

    def _policy(self):
        ok = self.sup.ok
        bms_lost = not (ok("BMS_Status") and ok("BMS_Measurements") and ok("BMS_Faults"))
        brake_lost = not (ok("BRAKE_Status") and ok("BRAKE_VehicleDynamics"))
        if bms_lost or (self.bms_fault and self.bms_sev >= 2):
            self.health = 2
        elif (brake_lost or self.brake_fault or self.speed_bad_ms > 500 or
              any(self.sup.sig_bad(k) for k in ("volt", "cur", "temp"))):
            self.health = 1
        else:
            self.health = 0
        self.cmd = self.req
        if self.health == 2:
            self.cmd = 0.0
        elif self.health == 1:
            self.cmd = max(-100.0, min(100.0, self.cmd))
        if self.brake_applied and self.cmd > 0.0:
            self.cmd = 0.0

    def step(self, t):
        if self.state == 1 and t >= 500:
            self.state = 2
        if self.every("status", 20, t):
            ps = self.published_state()
            self.send("PT_Status", phys=dict(PT_State=ps, PT_GearPosition=self.gear, PT_DriveMode=1,
                      PT_ReadyToDrive=int(ps in (2, 3)), PT_FaultActive=int(ps == 5)))
        if self.every("torque", 10, t):
            self.sup.tick()
            self._policy()
            self.act += (self.cmd - self.act) * 0.1
            self.rpm = min(12000.0, max(0.0, self.rpm + self.act * 0.02 - self.rpm * 0.002))
            self.send("PT_Torque", phys=dict(MotorTorqueRequest=self.cmd, MotorTorqueActual=self.act,
                                             MotorSpeed=self.rpm))
