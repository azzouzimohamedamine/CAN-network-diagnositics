"""Figures for Python SIL scenarios. Every figure is labelled SIMULATED."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

STATE = {1: "INIT", 2: "READY", 3: "DRIVE", 4: "DEGRADED", 5: "FAULT"}


def _events(r):
    seen, out = set(), []
    for t, _owner, text in r.sim.events:
        code = text.split()[1]
        kind = "set" if " set" in text else "healed"
        if (t, code, kind) not in seen:
            seen.add((t, code, kind))
            out.append((t, code, kind))
    return out


def plot_scenario(r, path):
    fig, ax = plt.subplots(3, 1, sharex=True, figsize=(9, 7.2))
    st = r.series("PT_Status", "PT_State")
    ax[0].step([t / 1000 for t, _, _ in st], [v for _, v, _ in st], where="post", color="tab:blue")
    ax[0].set_yticks(list(STATE))
    ax[0].set_yticklabels(list(STATE.values()))
    ax[0].set_ylabel("PT_State (0x100)")
    req, act = r.series("PT_Torque", "MotorTorqueRequest"), r.series("PT_Torque", "MotorTorqueActual")
    ax[1].plot([t / 1000 for t, _, _ in req], [v for _, v, _ in req], label="MotorTorqueRequest", color="tab:green")
    ax[1].plot([t / 1000 for t, _, _ in act], [v for _, v, _ in act], label="MotorTorqueActual", color="tab:olive", ls="--")
    ax[1].set_ylabel("Torque [Nm] (0x101)")
    ax[1].legend(loc="lower right", fontsize=8)
    for i, sig in enumerate(["Warn_Battery", "Warn_Brake", "Warn_Powertrain", "Warn_CommLoss"]):
        s = r.series("CLUSTER_Warning", sig)
        ax[2].step([t / 1000 for t, _, _ in s], [i + 0.8 * v for _, v, _ in s], where="post", label=sig)
    ax[2].set_yticks([0.4, 1.4, 2.4, 3.4])
    ax[2].set_yticklabels(["Battery", "Brake", "Powertrain", "CommLoss"])
    ax[2].set_ylabel("Cluster lamps (0x401)")
    ax[2].set_xlabel("simulated time [s]")
    for a in ax:
        for t0, t1, label in r.sim.windows:
            a.axvspan(t0 / 1000, t1 / 1000, color="orange", alpha=0.15)
        for t, code, kind in _events(r):
            a.axvline(t / 1000, color="red" if kind == "set" else "green", lw=1, ls=":")
    for t0, t1, label in r.sim.windows:
        ax[0].text(t0 / 1000, 5.45, label, fontsize=8, color="darkorange", va="bottom")
    for t, code, kind in _events(r):
        ax[0].text(t / 1000, 1.1 if kind == "set" else 1.5, f"DTC {code} {kind}", fontsize=7, rotation=90,
                   color="red" if kind == "set" else "green", ha="right")
    fig.suptitle(f"{r.name} - SIMULATED (Python SIL, not a vehicle or CANoe measurement)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(path, dpi=110)
    plt.close(fig)
