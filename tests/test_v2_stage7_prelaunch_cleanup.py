from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"


def test_v2_stale_prelaunch_cleanup_is_ported_without_auto_injection():
    policy = (STAGE / "core" / "prelaunch_policy.py").read_text(encoding="utf-8")
    steam = (STAGE / "core" / "steam.py").read_text(encoding="utf-8")
    patch = (STAGE / "patch" / "__init__.py").read_text(encoding="utf-8")

    for token in (
        "_WINDOWS_PRELAUNCH",
        "_POSIX_PRELAUNCH",
        "def strip_minify_prelaunch_prefix(",
        "removed_prelaunch",
        "removed_command_wrapper",
    ):
        assert token in policy

    assert "from core.prelaunch_policy import strip_minify_prelaunch_prefix" in steam
    assert "def remove_minify_prelaunch_from_launch_options(" in steam
    assert "strip_minify_prelaunch_prefix(launch_options)" in steam

    assert "fix_language_options = config.get(\"fix_options\", True)" in patch
    assert "prelaunch_cleanup_needed" in patch
    assert "prelaunch_removed" in patch
    assert "steam.remove_minify_prelaunch_from_launch_options(check_only=True)" in patch
    assert "steam.remove_minify_prelaunch_from_launch_options()" in patch
    assert "steam.add_prelaunch_to_launch_options(" not in patch


def test_v2_settings_preset_template_avoids_non_null_assertion_syntax():
    source = (
        STAGE / "ui" / "web" / "src" / "lib" / "components" / "Settings.svelte"
    ).read_text(encoding="utf-8")
    assert "items[0].mod!" not in source
    assert 'applyPreset(items[0].mod || "")' in source
