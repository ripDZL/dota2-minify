from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"


def test_v2_updater_tracks_fork_not_upstream_release_channel():
    updater = (STAGE / "ui" / "web" / "src" / "lib" / "updater.ts").read_text(encoding="utf-8")
    app = (STAGE / "ui" / "app.py").read_text(encoding="utf-8")

    assert 'https://api.github.com/repos/ripDZL/dota2-minify/releases' in updater
    assert 'https://github.com/ripDZL/dota2-minify/releases/tag/' in updater
    assert 'repos/Egezenn/dota2-minify/releases' not in updater
    assert 'github.com/Egezenn/dota2-minify/releases/tag/' not in updater

    assert "def get_version(self) -> str:" in app
    assert "return base.DISPLAY_VERSION" in app
