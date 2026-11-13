"""Python SIL scenario tests (TC-301..TC-310). Results are SIMULATED: they verify the supervision/degradation
DESIGN as ported to Python, not the CAPL source and not a vehicle. Expectations derive from the requirements
(timeouts = 3 x cycle, debounce 3/5, 500 ms speed hold), with the 10 ms supervision tick as tolerance."""
import pytest
from can_analysis.asc_log import parse_asc
from can_analysis.periodicity import analyze
from sil.scenarios import run

PT, CL = "POWERTRAIN_ECU", "CLUSTER_ECU"


def set_time(r, owner, text):
    ev = r.events(owner, text)
    assert ev, f"{owner}: '{text}' not found; events={r.sim.events}"
    return ev[0][0]


def test_tc301_nominal_no_dtc_and_periodicity_ok(tmp_path):
    r = run("nominal")
    assert r.sim.events == [] and r.at("PT_Status", "PT_State", 4000) == 3
    path = tmp_path / "nominal.asc"
    r.sim.write_asc(path)
    reps = analyze(list(parse_asc(open(path))), r.sim.db)
    assert len(reps) == 9
    for m in reps:
        assert m.period_ok and not m.timeout_gaps and m.crc_errors == 0 and m.counter_errors == 0, m


def test_tc302_f01_single_frame_loss_gives_no_dtc():
    r = run("f01_single_frame_loss")
    assert r.sim.events == []
    assert {s for t, s, _ in r.series("PT_Status", "PT_State") if t > 1700} == {3}


def test_tc303_f02_brake_timeout_detect_degrade_heal():
    r = run("f02_brake_timeout")
    for owner in (PT, CL):
        # last 0x200 frame at 2980 ms (20 ms cycle, drop from 3000): detected after > 60 ms, within one 10 ms tick
        assert 3040 < set_time(r, owner, "DTC D100 set") <= 3050
        assert 3500 <= set_time(r, owner, "DTC D100 healed") <= 3700    # 5 good frames after the window
    assert r.at("PT_Status", "PT_State", 3150) == 4 and r.at("PT_Status", "PT_State", 3400) == 4
    assert r.at("CLUSTER_Warning", "Warn_Brake", 3300) == 1 and r.at("CLUSTER_Warning", "Warn_CommLoss", 3300) == 1
    assert r.at("PT_Status", "PT_State", 3800) == 3 and r.at("CLUSTER_Warning", "Warn_Brake", 4000) == 0


def test_tc304_f05_bms_unavailable_fault_and_slow_recovery():
    r = run("f05_bms_unavailable")
    for owner in (PT, CL):
        assert 3100 <= set_time(r, owner, "DTC D101 set") <= 3140       # BMS_Measurements 150 ms timeout
    assert r.at("PT_Status", "PT_State", 3300) == 5 and r.at("PT_Torque", "MotorTorqueRequest", 3300) == 0
    assert r.at("CLUSTER_Warning", "Warn_Battery", 3300) == 1 and r.at("CLUSTER_Warning", "Warn_CommLoss", 3300) == 1
    # Finding: heal needs 5 good BMS_Faults frames at a 500 ms heartbeat -> about 2.5 s after the node returns
    assert r.at("PT_Status", "PT_State", 5500) == 5
    assert 6000 <= set_time(r, PT, "DTC D101 healed") <= 6600


@pytest.mark.parametrize("name,code,t_lo,t_hi", [("f07b_crc_fault", "D111", 3020, 3030),
                                                  ("f07a_counter_fault", "D110", 3020, 3030)])
def test_tc305_306_e2e_faults_confirm_after_three_frames(name, code, t_lo, t_hi):
    r = run(name)
    for owner in (PT, CL):
        assert t_lo <= set_time(r, owner, f"DTC {code} set") <= t_hi
        assert set_time(r, owner, f"DTC {code} healed") <= 3250
    assert r.at("PT_Status", "PT_State", 3400) == 3


def test_tc307_f03_speed_invalid_hold_then_degrade():
    r = run("f03_speed_invalid")
    assert 3000 <= set_time(r, PT, "DTC 5201 set") <= 3040
    assert r.at("PT_Status", "PT_State", 3400) == 3          # held < 500 ms: not degraded yet
    assert r.at("PT_Status", "PT_State", 3700) == 4          # > 500 ms: degraded
    assert r.at("CLUSTER_Status", "DisplayedSpeed", 3500, raw=True) == 255   # dashes immediately
    assert r.at("PT_Status", "PT_State", 4200) == 3


def test_tc308_f04_voltage_out_of_range_rejected():
    r = run("f04_voltage_out_of_range")
    assert 3000 <= set_time(r, PT, "DTC 1301 set") <= 3200
    assert r.at("PT_Status", "PT_State", 3300) == 4 and r.at("PT_Status", "PT_State", 4200) == 3


def test_tc309_brake_override_zeroes_torque_request():
    r = run("brake_override")
    assert r.at("PT_Torque", "MotorTorqueRequest", 3150) == 0
    assert r.at("PT_Torque", "MotorTorqueRequest", 4200) == pytest.approx(60, abs=0.1)


def test_tc310_runs_are_deterministic():
    a, b = run("f02_brake_timeout"), run("f02_brake_timeout")
    assert [(m.timestamp, m.arbitration_id, bytes(m.data)) for m in a.sim.bus.log] == \
           [(m.timestamp, m.arbitration_id, bytes(m.data)) for m in b.sim.bus.log]
