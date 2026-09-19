"""PyInstaller guards for unattended Windows CI builds."""

import os
import platform
from collections.abc import Callable, Iterable
from typing import Any


def should_skip_package_import_probe(
    platform_name: str | None = None,
    github_actions: str | None = None,
) -> bool:
    """Skip PyInstaller's DLL-path package import probe only on GitHub Windows runners."""
    current_platform = platform_name or platform.system()
    actions_flag = os.environ.get("GITHUB_ACTIONS", "") if github_actions is None else github_actions
    return current_platform == "Windows" and actions_flag.lower() == "true"


def filter_dynamic_import_packages(
    import_packages: Iterable[str],
    *,
    platform_name: str | None = None,
    github_actions: str | None = None,
) -> list[str]:
    """Keep binary scanning enabled while suppressing the CI-only package import heuristic."""
    packages = list(import_packages)
    if should_skip_package_import_probe(platform_name, github_actions):
        return []
    return packages


def make_find_binary_dependencies_guard(
    original: Callable[..., Any],
    *,
    platform_name: str | None = None,
    github_actions: str | None = None,
) -> Callable[..., Any]:
    """Wrap PyInstaller's dependency scan without changing its binary analysis."""
    def guarded(binaries, import_packages, symlink_suppression_patterns):
        packages = list(import_packages)
        filtered = filter_dynamic_import_packages(
            packages,
            platform_name=platform_name,
            github_actions=github_actions,
        )
        if packages and not filtered:
            print(
                "[PyInstaller guard] GitHub Windows runner: skipping the "
                f"package-import DLL-path probe for {len(packages)} packages; "
                "binary dependency analysis remains enabled.",
                flush=True,
            )
        return original(binaries, filtered, symlink_suppression_patterns)

    guarded._minify_dynamic_import_guard = True
    return guarded


def install_windows_ci_guard() -> None:
    """Install the guard before Analysis() is constructed by the spec file."""
    if not should_skip_package_import_probe():
        return

    from PyInstaller.building import build_main

    current = build_main.find_binary_dependencies
    if getattr(current, "_minify_dynamic_import_guard", False):
        return

    build_main.find_binary_dependencies = make_find_binary_dependencies_guard(current)
