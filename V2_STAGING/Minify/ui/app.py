import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import webview
from core import base, config, constants, output, security, utils

from ui.services import ConfigService, DialogService, ModService, PatchService, PluginService

UPDATE_MAX_BYTES = 512 * 1024 * 1024
WORKSHOP_TOOLS_MAX_BYTES = 1024 * 1024 * 1024
GITHUB_ALLOWED_HOSTS = {"github.com", "api.github.com"}


def _validate_github_https_url(url: str) -> None:
    security.validate_public_https_url(url)
    from urllib.parse import urlsplit

    host = str(urlsplit(url).hostname or "").rstrip(".").casefold()
    if host in GITHUB_ALLOWED_HOSTS or host.endswith(".githubusercontent.com"):
        return
    raise ValueError(f"Unexpected GitHub download host: {host or '(missing)'}")


def _fetch_bounded_json(url: str, *, max_bytes: int = 8 * 1024 * 1024):
    import json
    import requests

    _validate_github_https_url(url)
    response = requests.get(
        url,
        headers={"User-Agent": "dota2-minify"},
        stream=True,
        timeout=(10, 30),
        allow_redirects=False,
    )
    try:
        response.raise_for_status()
        try:
            declared = int(response.headers.get("content-length", 0) or 0)
        except (TypeError, ValueError):
            declared = 0
        if declared > max_bytes:
            raise ValueError("GitHub API response exceeds the safety limit.")

        payload = bytearray()
        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            payload.extend(chunk)
            if len(payload) > max_bytes:
                raise ValueError("GitHub API response exceeds the safety limit.")
        return json.loads(payload.decode("utf-8"))
    finally:
        response.close()


def _verify_sha256(path: str, expected: str) -> None:
    expected = str(expected or "").strip().casefold()
    if expected.startswith("sha256:"):
        expected = expected.split(":", 1)[1]
    if len(expected) != 64 or any(char not in "0123456789abcdef" for char in expected):
        raise ValueError("Missing or invalid SHA-256 digest.")
    actual = security.sha256_file(path).casefold()
    if actual != expected:
        raise ValueError(f"SHA-256 mismatch: expected {expected}, got {actual}.")


class Api:
    def __init__(self) -> None:
        self.patch_service = PatchService()
        self.mod_service = ModService()
        self.config_service = ConfigService()
        self.plugin_service = PluginService()
        self.dialog_service = DialogService()

    def set_window(self, window: Any) -> None:
        self.patch_service.set_window(window)

    def start_patch(self) -> Dict[str, Any]:
        return self.patch_service.start_patch()

    def start_uninstall(self, remove_everything: bool = False) -> Dict[str, Any]:
        return self.patch_service.start_uninstall(remove_everything)

    def open_url(self, url: str) -> None:
        import webbrowser

        webbrowser.open(url)

    def is_patching(self) -> bool:
        return self.patch_service.is_patching()

    def get_logs(self) -> List[Dict[str, Any]]:
        return self.patch_service.get_logs()

    def clear_logs(self) -> bool:
        return self.patch_service.clear_logs()

    def get_mods(self) -> List[Dict[str, Any]]:
        return self.mod_service.get_mods()

    def get_mod_details(self, mod_name: str, lang: str | None = None) -> Dict[str, Any]:
        return self.mod_service.get_mod_details(mod_name, lang)

    def set_mods(self, data: Dict[str, bool]) -> bool:
        return self.mod_service.set_mods(data)

    def set_mod_favorite(self, mod_name: str, value: bool) -> Dict[str, Any]:
        return self.mod_service.set_favorite(mod_name, value)

    def get_profiles(self) -> List[Dict[str, Any]]:
        return self.mod_service.get_profiles()

    def save_profile(self, name: str) -> Dict[str, Any]:
        return self.mod_service.save_profile(name)

    def apply_profile(self, name: str) -> Dict[str, Any]:
        return self.mod_service.apply_profile(name)

    def duplicate_profile(self, name: str) -> Dict[str, Any]:
        return self.mod_service.duplicate_profile(name)

    def delete_profile(self, name: str) -> Dict[str, Any]:
        return self.mod_service.delete_profile(name)

    def get_available_languages(self) -> List[str]:
        return self.config_service.get_available_languages()

    def is_debug_env(self) -> bool:
        return self.config_service.is_debug_env()

    def get_version(self) -> str:
        return base.VERSION

    @staticmethod
    def is_portable() -> bool:
        if not base.FROZEN:
            return True
        return not os.path.exists(os.path.join(os.path.dirname(sys.executable), "unins000.exe"))

    def perform_update(self, url: str, sha256: str | None = None) -> bool:
        if not base.is_win or self.is_portable():
            import webbrowser

            webbrowser.open(base.github_io)
            return False

        import tempfile
        import threading
        import time

        from core import fs, log

        try:
            _validate_github_https_url(url)
            installer_name = security.safe_download_filename(url, allowed_extensions={".exe"})
            if not sha256:
                raise ValueError("The update asset is missing its GitHub SHA-256 digest.")
        except Exception as exc:
            output.add_text(f"Refusing unsafe update: {exc}", msg_type="error")
            return False

        def _update_thread():
            temp_dir = os.environ.get("TEMP", os.environ.get("TMP", tempfile.gettempdir()))
            installer_path = os.path.join(temp_dir, installer_name)

            output.add_text(f"Downloading update: {installer_name}...")
            success = fs.download_file(
                url=url,
                target_path=installer_path,
                name=installer_name,
                task_id="app-update",
                emit_progress=True,
                max_bytes=UPDATE_MAX_BYTES,
                url_validator=_validate_github_https_url,
                max_redirects=5,
            )
            if not success or not os.path.exists(installer_path):
                output.add_text("Update download failed.", msg_type="error")
                return

            try:
                _verify_sha256(installer_path, sha256)
            except Exception as exc:
                fs.remove_path(installer_path)
                output.add_text(f"Update verification failed: {exc}", msg_type="error")
                return

            time.sleep(2)
            output.add_text("Launching verified installer and closing Minify...")
            try:
                os.startfile(installer_path)
            except Exception as exc:
                log.write_crashlog(f"Failed to launch installer: {exc}")
                output.add_text(f"Failed to launch installer: {exc}", msg_type="error")
                return
            os._exit(0)

        threading.Thread(target=_update_thread, daemon=True).start()
        return True

    def get_localization(self, lang: str = "en") -> Dict[str, str]:
        return self.config_service.get_localization(lang)

    def get_current_locale(self) -> str:
        return self.config_service.get_current_locale()

    def set_locale(self, lang: str) -> bool:
        return self.config_service.set_locale(lang)

    def get_available_game_languages(self) -> List[str]:
        return self.config_service.get_available_game_languages()

    def get_current_game_language(self) -> str:
        return self.config_service.get_current_game_language()

    def set_game_language(self, lang: str) -> bool:
        return self.config_service.set_game_language(lang)

    def get_steam_accounts(self) -> List[Dict[str, Any]]:
        return self.config_service.get_steam_accounts()

    def get_settings(self) -> Dict[str, Any]:
        return self.config_service.get_settings()

    def set_setting(self, key: str, value: Any, mod_name: str | None = None) -> bool:
        return self.config_service.set_setting(key, value, mod_name)

    def run_mod_function(self, mod_name: str, function_name: str) -> bool:
        return self.config_service.run_mod_function(mod_name, function_name)

    def reset_native_settings(self) -> bool:
        return self.config_service.reset_native_settings()

    def reset_mod_settings(self, mod_name: str) -> bool:
        return self.config_service.reset_mod_settings(mod_name)

    def get_available_themes(self) -> List[Dict[str, str]]:
        return self.config_service.get_available_themes()

    def get_theme_url(self, theme_name: str | None = None) -> str:
        return self.config_service.get_theme_url(theme_name)

    def get_theme_css(self, theme_name: str | None = None) -> str:
        return self.config_service.get_theme_css(theme_name)

    def get_state(self, key: str, default: Any = None) -> Any:
        states = utils.read_states()
        return states.get(key, default)

    def set_state(self, key: str, value: Any) -> bool:
        utils.write_states(key, value)
        return True

    def check_workshop_tools_needed(self) -> bool:
        import conditions

        return base.is_linux and not constants.rescomp_override and conditions.workshop_installed

    def extract_workshop_tools(self) -> bool:
        import helper

        return helper.extract_workshop_tools()

    def is_workshop_installed(self) -> bool:
        import conditions

        return bool(conditions.workshop_installed)

    def download_workshop_tools(self) -> bool:
        import tempfile

        import conditions
        from core import fs, log

        api_url = "https://api.github.com/repos/Dota-Modding-Community/workshoptools/releases/latest"
        zip_path = None
        staging_root = None
        backup_dir = None
        published = False
        try:
            payload = _fetch_bounded_json(api_url)
            assets = payload.get("assets", []) if isinstance(payload, dict) else []

            chosen = None
            for asset in assets[:128]:
                if not isinstance(asset, dict):
                    continue
                name = str(asset.get("name") or "")
                digest = str(asset.get("digest") or "")
                url = asset.get("browser_download_url")
                if name.casefold().endswith(".zip") and isinstance(url, str) and digest.casefold().startswith("sha256:"):
                    chosen = asset
                    break
            if not chosen:
                raise ValueError("Workshop Tools release has no ZIP asset with a SHA-256 digest.")

            download_url = str(chosen["browser_download_url"])
            expected_digest = str(chosen["digest"])
            _validate_github_https_url(download_url)

            temp_dir = os.environ.get("TEMP", os.environ.get("TMP", tempfile.gettempdir()))
            fd, zip_path = tempfile.mkstemp(prefix="minify-workshoptools-", suffix=".zip", dir=temp_dir)
            os.close(fd)

            output.add_text(f"Downloading Workshop Tools from {download_url}...")
            if not fs.download_file(
                url=download_url,
                target_path=zip_path,
                name=str(chosen.get("name") or "workshoptools.zip"),
                task_id="workshoptools",
                emit_progress=True,
                max_bytes=WORKSHOP_TOOLS_MAX_BYTES,
                url_validator=_validate_github_https_url,
                max_redirects=5,
            ):
                raise ValueError("Failed to download Workshop Tools.")
            _verify_sha256(zip_path, expected_digest)

            target_dir = os.path.abspath(base.rescomp_override_dir)
            parent = os.path.dirname(target_dir) or os.getcwd()
            fs.create_dirs(parent)
            if os.path.lexists(target_dir) and os.path.islink(target_dir):
                raise ValueError("Workshop Tools target cannot be a symlink.")

            staging_root = tempfile.mkdtemp(prefix=".minify-rescomp-stage-", dir=parent)
            payload_dir = os.path.join(staging_root, "rescomproot")
            fs.create_dirs(payload_dir)
            if not fs.extract_archive(zip_path, payload_dir):
                raise ValueError("Failed to safely extract Workshop Tools archive.")

            inner_dir = os.path.join(payload_dir, "resourcecompiler")
            if os.path.isdir(inner_dir) and not os.path.islink(inner_dir):
                for item in os.listdir(inner_dir):
                    source = os.path.join(inner_dir, item)
                    relative = security.safe_relative_path(item)
                    _, destination = security.confined_destination(payload_dir, relative)
                    if os.path.lexists(destination):
                        fs.remove_path(destination)
                    fs.move_path(source, destination)
                fs.remove_path(inner_dir)

            # Publish the fully extracted tree transactionally. Keep the prior
            # tree until the new compiler is verified through normal constants.
            if os.path.exists(target_dir):
                backup_dir = tempfile.mkdtemp(prefix=".minify-rescomp-backup-", dir=parent)
                fs.remove_path(backup_dir)
                os.replace(target_dir, backup_dir)
            os.replace(payload_dir, target_dir)
            published = True
            fs.remove_path(staging_root)
            staging_root = None

            constants.recalc_rescomp_dirs()
            compiler_exists = os.path.isfile(constants.dota_resource_compiler_path)
            if not compiler_exists:
                raise ValueError(
                    f"resourcecompiler was not found at {constants.dota_resource_compiler_path}"
                )

            if (base.is_linux or base.is_mac) and os.path.exists(constants.dota_resource_compiler_path):
                import stat

                mode = os.stat(constants.dota_resource_compiler_path, follow_symlinks=False).st_mode
                os.chmod(
                    constants.dota_resource_compiler_path,
                    mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
                )

            conditions.workshop_installed = True
            if backup_dir:
                fs.remove_path(backup_dir)
                backup_dir = None
            output.add_text("Workshop Tools installed successfully!", msg_type="success")
            return True
        except Exception as exc:
            log.write_crashlog(f"Error installing Workshop Tools: {exc}")
            output.add_text(f"Error installing Workshop Tools: {exc}", msg_type="error")

            # If publication happened but validation failed, restore the prior tree.
            target_dir = os.path.abspath(base.rescomp_override_dir)
            if published and os.path.exists(target_dir):
                try:
                    fs.remove_path(target_dir)
                except Exception as cleanup_exc:
                    log.write_crashlog(f"Workshop Tools staged-tree cleanup failed: {cleanup_exc}")
            if backup_dir and os.path.exists(backup_dir):
                try:
                    os.replace(backup_dir, target_dir)
                    backup_dir = None
                    constants.recalc_rescomp_dirs()
                except Exception as rollback_exc:
                    log.write_crashlog(f"Workshop Tools rollback failed: {rollback_exc}")
            return False
        finally:
            if zip_path:
                fs.remove_path(zip_path)
            if staging_root:
                fs.remove_path(staging_root)
            if backup_dir:
                # A backup left here means rollback could not complete; preserve it.
                log.write_warning(f"Workshop Tools recovery backup retained at {backup_dir}")

    def get_plugin_tabs(self) -> List[Dict[str, Any]]:
        return self.plugin_service.get_tabs(resolve_func=self._resolve_plugin_entry)

    def get_plugin_content(self, plugin_id: str) -> str:
        return self.plugin_service.get_content(plugin_id)

    def get_plugin_localization(self, plugin_id: str, lang: str = "en") -> Dict[str, str]:
        return self.plugin_service.get_localization(plugin_id, lang)

    def _resolve_plugin_entry(self, p_path: str) -> Optional[str]:
        return self.plugin_service._resolve_plugin_entry(p_path)

    def call_plugin_api(self, plugin_id: str, action: str, params: Dict[str, Any] = None) -> Any:
        return self.plugin_service.call_api(plugin_id, action, params)


def launch() -> None:
    if not os.path.isfile(base.dist_index):
        output.add_text(
            f"Error: Web UI build file not found at '{base.dist_index}'. Please run 'npm run build' inside Minify/ui/web.",
            msg_type="error",
        )

    debug_mode = bool(config.get("debug_env"))
    webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
    webview.settings["ALLOW_FILE_URLS"] = True

    url = Path(base.dist_index).as_uri()

    states = utils.read_states()
    window_size = states.get("window_size", {}) if isinstance(states, dict) else {}
    initial_width = window_size.get("width", 960)
    initial_height = window_size.get("height", 680)

    if not isinstance(initial_width, int) or initial_width < 700:
        initial_width = 960
    if not isinstance(initial_height, int) or initial_height < 500:
        initial_height = 680

    api = Api()
    active_theme = config.get("theme", "light")
    theme_css = api.get_theme_css(active_theme)
    bg_color = api.config_service.extract_bg_color(theme_css)
    window = webview.create_window(
        title=base.TITLE,
        url=url,
        js_api=api,
        width=initial_width,
        height=initial_height,
        min_size=(700, 500),
        resizable=True,
        background_color=bg_color,
    )

    def _save_window_size(*args: Any, **kwargs: Any) -> None:
        w, h = None, None
        if len(args) >= 2:
            w, h = args[0], args[1]
        if w and h and isinstance(w, (int, float)) and isinstance(h, (int, float)):
            w_int, h_int = int(w), int(h)
            if w_int >= 700 and h_int >= 500:
                utils.write_states("window_size", {"width": w_int, "height": h_int})

    window.events.resized += _save_window_size

    # to prevent MSHTML
    if not is_webview_available():
        _show_missing_dialog()
        return

    api.set_window(window)
    try:
        webview.start(debug=debug_mode, icon=base.favicon_file)
    except Exception:
        if not is_webview_available():
            _show_missing_dialog()
            return
        raise


def is_webview_available() -> bool:
    if base.is_win:
        return is_webview2_installed()
    try:
        return bool(webview.initialize())
    except Exception:
        return False


def is_webview2_installed() -> bool:
    import winreg

    guids = [
        "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",  # Microsoft Edge WebView2 Runtime
        "{2CD8A007-E189-409D-A2C8-9AF4EF3C72AA}",  # WebView2 Beta
        "{0D50BFEC-CD6A-4F9A-964C-C7416E3ACB10}",  # WebView2 Dev
        "{65C35B14-6C1D-4122-AC46-7148CC9D6497}",  # WebView2 Canary
    ]
    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for guid in guids:
            for sub in (
                rf"SOFTWARE\Microsoft\EdgeUpdate\Clients\{guid}",
                rf"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{guid}",
            ):
                try:
                    with winreg.OpenKey(root, sub) as key:
                        val, _ = winreg.QueryValueEx(key, "pv")
                        if val and val != "0.0.0.0":
                            return True
                except OSError:
                    pass
    return False


def _show_missing_dialog() -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox
        import webbrowser

        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", 1)

        if base.is_win:
            url = "https://developer.microsoft.com/en-us/microsoft-edge/webview2/"
            msg = (
                "Microsoft Edge WebView2 Runtime is required to run the GUI, but it is not installed.\n\n"
                f"Please install it from:\n{url}\n\n"
                "Also, you can install it via terminal:\n"
                "winget install -e --id Microsoft.EdgeWebView2Runtime\n\n"
                "Would you like to open the download page now?"
            )
            if messagebox.askyesno("WebView2 Required", msg):
                webbrowser.open(url)
        else:
            messagebox.showerror("Error", "WebView is not available on this system.")
        root.destroy()
    except Exception:
        pass
