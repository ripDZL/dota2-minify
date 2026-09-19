import importlib.util
from pathlib import Path


GUARD_PATH = Path(__file__).resolve().parents[1] / "V2_STAGING" / "scripts" / "pyinstaller_guard.py"


def _load_guard():
    spec = importlib.util.spec_from_file_location("v2_pyinstaller_guard", GUARD_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_windows_github_actions_skips_only_package_import_probe():
    guard = _load_guard()
    seen = {}

    def original(binaries, import_packages, symlink_suppression_patterns):
        seen["binaries"] = binaries
        seen["packages"] = list(import_packages)
        seen["patterns"] = symlink_suppression_patterns
        return "scanned"

    wrapped = guard.make_find_binary_dependencies_guard(
        original,
        platform_name="Windows",
        github_actions="true",
    )
    binaries = [("demo.dll", ".")]
    patterns = {"demo.dll"}

    assert wrapped(binaries, ["webview", "clr"], patterns) == "scanned"
    assert seen == {
        "binaries": binaries,
        "packages": [],
        "patterns": patterns,
    }


def test_guard_preserves_normal_package_probe_outside_windows_ci():
    guard = _load_guard()
    packages = ["webview", "clr"]

    assert guard.filter_dynamic_import_packages(
        packages,
        platform_name="Linux",
        github_actions="true",
    ) == packages
    assert guard.filter_dynamic_import_packages(
        packages,
        platform_name="Windows",
        github_actions="false",
    ) == packages
