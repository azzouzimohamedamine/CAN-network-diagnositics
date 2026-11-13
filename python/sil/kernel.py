"""Deterministic discrete-time simulation kernel (1 ms steps, simulated clock) and a minimal CAN bus model.
python-can is used for Message objects and ASC logging. A simulated clock (instead of the real-time python-can
'virtual' interface) is used on purpose: repeatable results, no OS timer jitter (Windows ~15 ms), fast tests.
Not modelled: arbitration, bit timing, error frames."""
from collections import defaultdict
from pathlib import Path
import can
import cantools
from can_analysis import e2e
from .supervision import DtcStore, Supervisor

DBC = Path(__file__).resolve().parents[2] / "can_database" / "vehicle_v1_0.dbc"


class Codec:
    def __init__(self, db):
        self.db = db
        self.names = {m.frame_id: m.name for m in db.messages}

    def encode(self, name, phys=None, raw=None):
        m, phys, raw, vals = self.db.get_message_by_name(name), phys or {}, raw or {}, {}
        for s in m.signals:
            if s.name in raw:
                vals[s.name] = int(raw[s.name])
            elif s.name in phys:
                vals[s.name] = int(round((phys[s.name] - s.offset) / s.scale))
            else:
                vals[s.name] = 0
        return bytearray(m.encode(vals, scaling=False, strict=False))

    def decode(self, can_id, data):
        m = self.db.get_message_by_frame_id(can_id)
        return m.name, m.decode(bytes(data), decode_choices=False, scaling=False)

    def phys(self, msg, sig, raw):
        s = self.db.get_message_by_name(msg).get_signal_by_name(sig)
        return raw * s.scale + s.offset

    def timeout(self, name):
        return self.db.get_message_by_name(name).dbc.attributes["MsgTimeoutMs"].value


class Bus:
    def __init__(self):
        self.now, self.pending, self.log, self.interceptors = 0, [], [], []

    def transmit(self, sender, msg):
        msg.timestamp = self.now / 1000.0
        for fn in self.interceptors:             # fault injection acts on the wire, never inside an ECU
            msg = fn(msg, sender)
            if msg is None:
                return
        self.log.append(msg)
        self.pending.append((sender, msg))


class Ecu:
    NAME = ""

    def __init__(self, sim):
        self.sim, self.codec, self.enabled = sim, sim.codec, True
        self.cnt, self.due = defaultdict(int), {}
        self.dtc = DtcStore(self.NAME, sim)
        self.sup = Supervisor(self.dtc)
        self.handlers = {}

    def every(self, key, period, t, first=None):
        if t >= self.due.get(key, period if first is None else first):
            self.due[key] = t + period
            return True
        return False

    def send(self, name, phys=None, raw=None):
        data = self.codec.encode(name, phys, raw)
        e2e.protect(data, self.cnt[name])
        self.cnt[name] = (self.cnt[name] + 1) & 0x0F
        mid = self.codec.db.get_message_by_name(name).frame_id
        self.sim.bus.transmit(self, can.Message(arbitration_id=mid, data=bytes(data), is_extended_id=False,
                                                channel=1, is_rx=False))

    def on_message(self, msg):
        name = self.codec.names.get(msg.arbitration_id)
        if name in self.handlers:
            if self.sup.on_rx(name, msg.data):
                self.handlers[name](self.codec.decode(msg.arbitration_id, msg.data)[1])

    def step(self, t):
        pass


class Simulation:
    def __init__(self):
        self.db = cantools.database.load_file(DBC, strict=True)
        self.codec, self.bus, self.nodes, self.events, self.schedule = Codec(self.db), Bus(), {}, [], []

    def add(self, cls):
        node = cls(self)
        self.nodes[node.NAME] = node
        return node

    def at(self, t_ms, fn):
        self.schedule.append((t_ms, fn))

    def run(self, duration_ms):
        for t in range(duration_ms + 1):
            self.bus.now = t
            for ts, fn in self.schedule:
                if ts == t:
                    fn(self)
            for n in self.nodes.values():
                if n.enabled:
                    n.step(t)
            while self.bus.pending:
                batch, self.bus.pending = self.bus.pending, []
                for sender, msg in batch:
                    for n in self.nodes.values():
                        if n.enabled and n is not sender:
                            n.on_message(msg)

    def write_asc(self, path):
        with can.ASCWriter(str(path)) as w:
            for m in self.bus.log:
                w.on_message_received(m)
