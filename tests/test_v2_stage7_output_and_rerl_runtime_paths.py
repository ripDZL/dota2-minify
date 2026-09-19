from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"


def test_v2_custom_output_path_is_not_overwritten_on_startup():
    helper = (STAGE / "helper.py").read_text(encoding="utf-8")
    service = (STAGE / "ui" / "services" / "config_service.py").read_text(encoding="utf-8")

    assert "def sync_output_path(force_locale=False):" in helper
    assert 'configured = config.get("output_path", "")' in helper
    assert "if not force_locale and isinstance(configured, str) and configured.strip():" in helper
    assert "os.path.abspath(os.path.expanduser(configured.strip()))" in helper
    assert "return output_path" in helper

    assert "helper.sync_output_path(force_locale=True)" in service
    assert 'elif key == "output_path":' in service
    assert "helper.sync_output_path()" in service


def test_v2_rerl_redirects_do_not_require_workshop_tools():
    patch = (STAGE / "patch" / "__init__.py").read_text(encoding="utf-8")
    rerl_assignment = patch.index('rerl_file = os.path.join(mod_path, "rerl.json")')
    workshop_branch = patch.index("if conditions.workshop_installed:", rerl_assignment)
    rerl_process = patch.index("if os.path.exists(rerl_file):", workshop_branch)

    assert rerl_assignment < workshop_branch < rerl_process
    assert "rerl_processor.process(rerl_file, folder, dota_pak_contents)" in patch
