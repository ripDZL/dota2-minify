from core import base
from patch import manifest_utils


def test_hardening_build_identity():
    assert base.VERSION == "1.14rc7"
    assert base.FORK_BUILD == "v21.4-hardening"
    assert base.TITLE == "Minify 1.14rc7 — v21.4-hardening"


def test_hardening_version_remains_manifest_compatible():
    assert manifest_utils.is_version_at_least(base.VERSION, ">=1.14rc7") is True
    assert manifest_utils.is_version_at_least(base.VERSION, ">=1.15") is False
