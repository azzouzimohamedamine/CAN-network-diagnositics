"""Python port of capl/common/dtc.cin + supervision.cin (same debounce: confirm 3, heal 5; 10 ms tick; 1 s startup grace)."""
from can_analysis import e2e

DTC_U1100, DTC_U1101, DTC_U1102, DTC_U1103 = 0xD100, 0xD101, 0xD102, 0xD103
DTC_U1110, DTC_U1111, DTC_U1112 = 0xD110, 0xD111, 0xD112
DTC_C1201, DTC_P1301, DTC_P1302, DTC_P1303 = 0x5201, 0x1301, 0x1302, 0x1303
FT_MISSING, FT_INVALID, FT_COUNTER, FT_PROTECTION = 0x87, 0x86, 0x82, 0x83
DEBOUNCE_FAIL, DEBOUNCE_HEAL, GRACE_MS, TICK_MS = 3, 5, 1000, 10


class DtcStore:
    def __init__(self, owner, sim):
        self.owner, self.sim, self.items = owner, sim, {}

    def _log(self, text):
        self.sim.events.append((self.sim.bus.now, self.owner, text))

    def set_failed(self, code, ftype):
        it = self.items.setdefault(code, {"ftype": ftype, "status": 0})
        if not it["status"] & 0x01:
            self._log(f"DTC {code:04X} set (failure type {ftype:02X})")
        it["status"] |= 0x09

    def set_passed(self, code):
        it = self.items.get(code)
        if it and it["status"] & 0x01:
            it["status"] &= 0xFE
            self._log(f"DTC {code:04X} healed")

    def is_failed(self, code):
        return bool(self.items.get(code, {}).get("status", 0) & 0x01)

    def confirmed(self):
        return sorted(c for c, i in self.items.items() if i["status"] & 0x08)


class Supervisor:
    def __init__(self, store):
        self.store, self.now, self.mon, self.sig = store, 0, {}, {}

    def add(self, name, timeout_ms, dtc):
        self.mon[name] = dict(timeout=timeout_ms, dtc=dtc, last=0, seen=False, prev=0, fail=0, good=0,
                              e2e_fault=False, timed_out=False)

    def _still_failing(self, code, except_name):
        return any(n != except_name and m["dtc"] == code and m["timed_out"] for n, m in self.mon.items())

    def on_rx(self, name, data):
        m = self.mon[name]
        st = e2e.verify(bytes(data), m["prev"] if m["seen"] else None)
        m["last"], m["seen"], m["prev"] = self.now, True, data[6] & 0x0F
        if st != e2e.E2EStatus.OK:
            m["good"] = 0
            m["fail"] += 1
            if m["fail"] >= DEBOUNCE_FAIL:
                m["e2e_fault"] = True
                if st == e2e.E2EStatus.CRC_ERROR:
                    self.store.set_failed(DTC_U1111, FT_PROTECTION)
                else:
                    self.store.set_failed(DTC_U1110, FT_COUNTER)
            return False
        m["fail"] = 0
        m["good"] += 1
        if m["good"] >= DEBOUNCE_HEAL:
            if m["e2e_fault"]:
                m["e2e_fault"] = False
                if not any(x["e2e_fault"] for x in self.mon.values()):
                    self.store.set_passed(DTC_U1110)
                    self.store.set_passed(DTC_U1111)
            if m["timed_out"]:
                m["timed_out"] = False
                if not self._still_failing(m["dtc"], name):
                    self.store.set_passed(m["dtc"])
        return True

    def tick(self):
        self.now += TICK_MS
        if self.now < GRACE_MS:
            return
        for m in self.mon.values():
            if m["timeout"] > 0 and not m["timed_out"] and self.now - m["last"] > m["timeout"]:
                m.update(timed_out=True, good=0, fail=0, seen=False)
                self.store.set_failed(m["dtc"], FT_MISSING)

    def ok(self, name):
        m = self.mon[name]
        return not (m["timed_out"] or m["e2e_fault"])

    def check_signal(self, key, raw, invalid, lo, hi, dtc, ftype=FT_INVALID):
        s = self.sig.setdefault(key, dict(fail=0, good=0, bad=False))
        if raw == invalid or raw < lo or raw > hi:
            s["good"] = 0
            s["fail"] += 1
            if s["fail"] >= DEBOUNCE_FAIL:
                s["bad"] = True
                self.store.set_failed(dtc, ftype)
            return False
        s["fail"] = 0
        s["good"] += 1
        if s["bad"] and s["good"] >= DEBOUNCE_HEAL:
            s["bad"] = False
            self.store.set_passed(dtc)
        return True

    def sig_bad(self, key):
        return self.sig.get(key, {}).get("bad", False)
