from unittest.mock import MagicMock

from core import base
from core.prelaunch_policy import strip_minify_prelaunch_prefix
from core.steam import add_prelaunch_to_launch_options, remove_minify_prelaunch_from_launch_options


def test_auto_prelaunch_injection_is_disabled():
    assert add_prelaunch_to_launch_options() is False
    assert add_prelaunch_to_launch_options(check_only=True) is False


def test_auto_prelaunch_injection_does_not_touch_steam(monkeypatch):
    mock_accounts = MagicMock(side_effect=AssertionError("Steam accounts should not be read"))
    mock_config = MagicMock(side_effect=AssertionError("Config should not be read"))
    monkeypatch.setattr("core.steam.get_steam_accounts", mock_accounts)
    monkeypatch.setattr("core.steam.config.get", mock_config)

    assert add_prelaunch_to_launch_options() is False
    mock_accounts.assert_not_called()
    mock_config.assert_not_called()


def test_strip_windows_minify_prelaunch_prefix():
    options = 'cmd /c "C:\\Tools\\Minify.exe" prelaunch && %command% -novid -language english'

    cleaned, changed = strip_minify_prelaunch_prefix(options)

    assert changed is True
    assert cleaned == "-novid -language english"


def test_strip_posix_minify_prelaunch_prefix():
    options = 'bash -c "/opt/Minify prelaunch" && %command% -novid'

    cleaned, changed = strip_minify_prelaunch_prefix(options)

    assert changed is True
    assert cleaned == "-novid"


def test_strip_orphaned_command_wrapper_with_dota_args():
    cleaned, changed = strip_minify_prelaunch_prefix("%command% -novid +fps_max 120")

    assert changed is True
    assert cleaned == "-novid +fps_max 120"


def test_unrelated_user_wrapper_is_untouched():
    options = "WAYLAND=1 mangohud %command% -novid"

    cleaned, changed = strip_minify_prelaunch_prefix(options)

    assert changed is False
    assert cleaned == options


def _mock_steam_launch_options(monkeypatch, launch_options, *, apply_for_all=True):
    data = {
        "UserLocalConfigStore": {
            "Software": {
                "Valve": {"Steam": {"apps": {base.STEAM_DOTA_ID: {"LaunchOptions": launch_options}}}}
            }
        }
    }

    monkeypatch.setattr("core.steam.get_steam_accounts", lambda: [{"id": "123", "name": "User"}])

    def config_get(key, default=None):
        values = {
            "apply_for_all": apply_for_all,
            "steam_id": "123",
            "steam_root": "/fake/steam",
        }
        return values.get(key, default)

    monkeypatch.setattr("core.steam.config.get", config_get)
    monkeypatch.setattr("core.steam.os.path.exists", lambda path: True)
    monkeypatch.setattr("core.steam.utils.open_utf8R", MagicMock())
    monkeypatch.setattr("core.steam.vdf.load", lambda file: data)
    mock_dump = MagicMock()
    monkeypatch.setattr("core.steam.vdf.dump", mock_dump)
    return data, mock_dump


def _launch_options(data):
    return data["UserLocalConfigStore"]["Software"]["Valve"]["Steam"]["apps"][base.STEAM_DOTA_ID][
        "LaunchOptions"
    ]


def test_cleanup_removes_generated_windows_prelaunch(monkeypatch):
    data, mock_dump = _mock_steam_launch_options(
        monkeypatch,
        'cmd /c "C:\\Old Minify\\Minify.exe" prelaunch && %command% -novid -language english',
    )

    changed = remove_minify_prelaunch_from_launch_options()

    assert changed is True
    assert mock_dump.called
    assert _launch_options(data) == "-novid -language english"


def test_cleanup_check_only_reports_without_mutating(monkeypatch):
    original = 'bash -c "/opt/Minify prelaunch" && %command% -novid'
    data, mock_dump = _mock_steam_launch_options(monkeypatch, original)

    changed = remove_minify_prelaunch_from_launch_options(check_only=True)

    assert changed is True
    assert not mock_dump.called
    assert _launch_options(data) == original


def test_cleanup_does_not_remove_unrelated_user_wrapper(monkeypatch):
    original = "WAYLAND=1 mangohud %command% -novid"
    data, mock_dump = _mock_steam_launch_options(monkeypatch, original)

    changed = remove_minify_prelaunch_from_launch_options()

    assert changed is False
    assert not mock_dump.called
    assert _launch_options(data) == original


def test_cleanup_honors_single_selected_account(monkeypatch):
    data, mock_dump = _mock_steam_launch_options(
        monkeypatch,
        'cmd /c "C:\\Tools\\Minify.exe" prelaunch && %command% -novid',
        apply_for_all=False,
    )

    changed = remove_minify_prelaunch_from_launch_options()

    assert changed is True
    assert mock_dump.called
    assert _launch_options(data) == "-novid"
