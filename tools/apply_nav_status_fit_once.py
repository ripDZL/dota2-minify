from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "Minify" / "__main__.py"
WINDOW = ROOT / "Minify" / "ui" / "window.py"
TESTS = ROOT / "tests" / "test_modern_ui.py"


def once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"missing anchor: {label}")
    return text.replace(old, new, 1)


main = MAIN.read_text(encoding="utf-8")
main = once(
    main,
    '            tag="nav_status_card",\n            width=-1,\n            height=54,',
    '            tag="nav_status_card",\n            width=-1,\n            height=66,',
    "nav status initial height",
)
MAIN.write_text(main, encoding="utf-8")

window = WINDOW.read_text(encoding="utf-8")
window = once(
    window,
    "    shell_body_height = max(350, min(500, int(shared.window_height * 0.47)))\n    workspace_width = max(430, shared.window_width - nav_width - 34)",
    "    shell_body_height = max(350, min(500, int(shared.window_height * 0.47)))\n    nav_status_height = 66 if shell_body_height >= 370 else 62\n    workspace_width = max(430, shared.window_width - nav_width - 34)",
    "nav status responsive height",
)
window = once(
    window,
    '    if dpg.does_item_exist("app_nav_rail"):\n        dpg.configure_item("app_nav_rail", width=nav_width, height=shell_body_height)\n    if dpg.does_item_exist("app_workspace"):',
    '    if dpg.does_item_exist("app_nav_rail"):\n        dpg.configure_item("app_nav_rail", width=nav_width, height=shell_body_height)\n    if dpg.does_item_exist("nav_status_card"):\n        dpg.configure_item("nav_status_card", height=nav_status_height)\n    if dpg.does_item_exist("app_workspace"):',
    "nav status resize wiring",
)
WINDOW.write_text(window, encoding="utf-8")

tests = TESTS.read_text(encoding="utf-8")
addition = '''\n\ndef test_nav_status_card_has_safe_vertical_budget():\n    start = MAIN.index('tag="nav_status_card"')\n    card = MAIN[start : start + 240]\n    assert "height=66" in card\n    assert "nav_status_height = 66 if shell_body_height >= 370 else 62" in WINDOW\n    assert 'dpg.configure_item("nav_status_card", height=nav_status_height)' in WINDOW\n'''
if "def test_nav_status_card_has_safe_vertical_budget():" not in tests:
    tests += addition
TESTS.write_text(tests, encoding="utf-8")
