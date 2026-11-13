from reporting.sil_report import build


def test_tc311_report_and_figures_are_generated(tmp_path):
    figs = tmp_path / "figures"
    figs.mkdir()
    build(figs, tmp_path / "sil_results.md")
    text = (tmp_path / "sil_results.md").read_text()
    assert "SIMULATED" in text and "DTC D100 set @ 3050 ms" in text
    assert len(list(figs.glob("sil_*.png"))) == 9
