"""Scenarios for the Python SIL. Faults are injected ON THE WIRE (bus interceptors) or by disabling a node -
ECU code contains no test hooks (FLT-REQ-004). All results are SIMULATED (Python port of the CAPL design)."""
import can
from can_analysis import e2e
from .kernel import Simulation
from .ecus import PowertrainEcu, BrakeEcu, BmsEcu, ClusterEcu

ID = {"PT_Status": 0x100, "PT_Torque": 0x101, "BRAKE_Status": 0x200, "BRAKE_VehicleDynamics": 0x201,
      "CLUSTER_Status": 0x400, "CLUSTER_Warning": 0x401,
      "BMS_Status": 0x300, "BMS_Measurements": 0x301, "BMS_Faults": 0x302}


def _window(sim, t0, t1):
    return t0 <= sim.bus.now < t1


def drop(sim, can_id, t0, t1):
    sim.bus.interceptors.append(lambda m, s: None if m.arbitration_id == can_id and _window(sim, t0, t1) else m)


def drop_once(sim, can_id, t0):
    state = {"done": False}

    def fn(m, s):
        if m.arbitration_id == can_id and sim.bus.now >= t0 and not state["done"]:
            state["done"] = True
            return None
        return m
    sim.bus.interceptors.append(fn)


def _rebuild(sim, m, data):
    return can.Message(arbitration_id=m.arbitration_id, data=bytes(data), is_extended_id=False,
                       channel=m.channel, is_rx=False)


def corrupt_crc(sim, can_id, t0, t1):
    def fn(m, s):
        if m.arbitration_id == can_id and _window(sim, t0, t1):
            d = bytearray(m.data)
            d[7] ^= 0xFF
            return _rebuild(sim, m, d)
        return m
    sim.bus.interceptors.append(fn)


def freeze_counter(sim, can_id, t0, t1, value=3):
    def fn(m, s):
        if m.arbitration_id == can_id and _window(sim, t0, t1):
            return _rebuild(sim, m, e2e.protect(bytearray(m.data), value))   # CRC stays valid
        return m
    sim.bus.interceptors.append(fn)


def set_raw(sim, can_id, t0, t1, **raw):
    def fn(m, s):
        if m.arbitration_id == can_id and _window(sim, t0, t1):
            name, vals = sim.codec.decode(can_id, m.data)
            vals.update(raw)
            d = sim.codec.encode(name, raw=vals)
            return _rebuild(sim, m, e2e.protect(d, m.data[6] & 0x0F))
        return m
    sim.bus.interceptors.append(fn)


class Result:
    def __init__(self, sim, name):
        self.sim, self.name = sim, name

    def series(self, msg, sig):
        out = []
        for m in self.sim.bus.log:
            if m.arbitration_id == ID[msg]:
                _, raw = self.sim.codec.decode(m.arbitration_id, m.data)
                out.append((round(m.timestamp * 1000), self.sim.codec.phys(msg, sig, raw[sig]), raw[sig]))
        return out

    def at(self, msg, sig, t_ms, raw=False):
        last = None
        for t, p, r in self.series(msg, sig):
            if t > t_ms:
                break
            last = r if raw else p
        return last

    def events(self, owner=None, text=None):
        return [e for e in self.sim.events if (owner is None or e[1] == owner) and (text is None or text in e[2])]


def build(name):
    sim = Simulation()
    sim.windows = []          # (t0_ms, t1_ms, label) of injected faults, used for plots/reports
    pt, br = sim.add(PowertrainEcu), sim.add(BrakeEcu)
    sim.add(BmsEcu)
    sim.add(ClusterEcu)
    sim.at(1200, lambda s: pt.press("s"))
    for i in range(3):
        sim.at(1500 + 100 * i, lambda s: pt.press("u"))
    dur = 5000
    if name == "nominal":
        pass
    elif name == "f01_single_frame_loss":
        drop_once(sim, ID["BRAKE_Status"], 3000)
        sim.windows.append((3000, 3020, "one 0x200 frame dropped"))
    elif name == "f02_brake_timeout":
        drop(sim, ID["BRAKE_Status"], 3000, 3500)
        sim.windows.append((3000, 3500, "0x200 BRAKE_Status absent"))
    elif name == "f03_speed_invalid":
        set_raw(sim, ID["BRAKE_VehicleDynamics"], 3000, 3800, VehicleSpeed=65535)
        sim.windows.append((3000, 3800, "VehicleSpeed = invalid (0xFFFF)"))
    elif name == "f04_voltage_out_of_range":
        set_raw(sim, ID["BMS_Measurements"], 3000, 3500, BatteryVoltage=6000)
        sim.windows.append((3000, 3500, "BatteryVoltage = 600 V"))
    elif name == "f05_bms_unavailable":
        sim.at(3000, lambda s: setattr(s.nodes["BMS_ECU"], "enabled", False))
        sim.at(4500, lambda s: setattr(s.nodes["BMS_ECU"], "enabled", True))
        sim.windows.append((3000, 4500, "BMS_ECU unavailable"))
        dur = 6500
    elif name == "f07a_counter_fault":
        freeze_counter(sim, ID["BRAKE_VehicleDynamics"], 3000, 3100)
        sim.windows.append((3000, 3100, "alive counter frozen on 0x201"))
    elif name == "f07b_crc_fault":
        corrupt_crc(sim, ID["BRAKE_VehicleDynamics"], 3000, 3100)
        sim.windows.append((3000, 3100, "CRC corrupted on 0x201"))
    elif name == "brake_override":
        sim.at(3000, lambda s: br.press("b"))
        sim.at(4000, lambda s: br.press("b"))
        sim.windows.append((3000, 4000, "brake pedal applied"))
    else:
        raise ValueError(name)
    return sim, dur


SCENARIOS = ["nominal", "f01_single_frame_loss", "f02_brake_timeout", "f03_speed_invalid",
             "f04_voltage_out_of_range", "f05_bms_unavailable", "f07a_counter_fault", "f07b_crc_fault",
             "brake_override"]


def run(name):
    sim, dur = build(name)
    sim.run(dur)
    return Result(sim, name)
