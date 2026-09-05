from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "Minify" / "__main__.py").read_text(encoding="utf-8")
THEME = (ROOT / "Minify" / "ui" / "theme.py").read_text(encoding="utf-8")
WINDOW = (ROOT / "Minify" / "ui" / "window.py").read_text(encoding="utf-8")


def test_stale_workspace_badge_removed():
    assert "LOCAL MOD WORKSPACE" not in MAIN
    assert 'dpg.add_text("RC6"' not in MAIN
    assert 'tag="header_context"' not in MAIN
    assert 'tag="header_badge"' not in MAIN
    assert '"header_spacer"' not in WINDOW


def test_modern_graphite_blue_palette_is_materialized():
    assert "# v21.4: modern graphite visual system." in THEME
    assert "ACCENT = (80, 145, 255, 255)" in THEME
    assert "BEVEL_DARK = (0, 0, 0, 0)" in THEME
    assert "mvStyleVar_FrameRounding, 7" in THEME
    assert "mvStyleVar_ChildRounding, 9" in THEME
