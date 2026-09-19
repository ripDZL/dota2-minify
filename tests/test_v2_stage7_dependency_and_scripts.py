from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"


def test_v2_dependency_downloads_are_verified_and_arch_safe():
    constants = (STAGE / "core" / "constants.py").read_text(encoding="utf-8")
    conditions = (STAGE / "conditions.py").read_text(encoding="utf-8")

    assert "s2v_latest = None" in constants
    assert "rg_latest = None" in constants
    assert "powerpc64-unknown-linux-gnu" not in constants
    assert "i686-unknown-linux-gnu" not in constants
    assert 'base.MACHINE in ["amd64", "x86_64", "aarch64", "arm64"]' in constants

    assert "security.verify_expected_download(zip_path, constants.s2v_latest)" in conditions
    assert "security.verify_expected_download(archive_path, constants.rg_latest)" in conditions
    assert 'if not constants.s2v_latest:' in conditions
    assert 'if not constants.rg_latest:' in conditions
    assert "No verified automatic" in conditions


def test_v2_lifecycle_scripts_use_logical_ids_for_nested_mods():
    helper = (STAGE / "helper.py").read_text(encoding="utf-8")
    for token in (
        "for mod_name in list(mods_shared.mods_with_order):",
        "mod_path = mods_shared.get_mod_path(mod_name)",
        "mods_shared.get_state(mod_name)",
        're.sub(r"[^a-zA-Z0-9_]+"',
        'module_name = safe_mod_name + f"_{order_name}_script"',
        'module_name = safe_mod_name + "_utility"',
    ):
        assert token in helper

    assert "mods_shared.get_state(os.path.basename(root))" not in helper
