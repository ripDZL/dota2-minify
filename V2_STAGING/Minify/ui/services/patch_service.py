import json
import os
import threading
import time
from typing import Any, Dict, List

import patch
from core import backup_manager, mod_compat, mod_library, mods_shared, output
from patch import manifest_utils


class PatchService:
    def __init__(self) -> None:
        self._window: Any = None
        self._is_patching: bool = False
        self._logs: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

        output.register_listener(self._on_output_log)
        output.register_download_listener(self._on_download_progress)

    def set_window(self, window: Any) -> None:
        self._window = window

    def _on_download_progress(self, data: Dict[str, Any]) -> None:
        if self._window:
            try:
                js_str = json.dumps(data)
                self._window.evaluate_js(f"window.onDownloadProgress && window.onDownloadProgress({js_str});")
            except Exception:
                pass

    def _on_output_log(self, text: str, msg_type: str | None) -> None:
        if msg_type == "clear":
            with self._lock:
                self._logs.clear()
            if self._window:
                try:
                    self._window.evaluate_js("window.onLogReceived && window.onLogReceived({text: '', type: 'clear'});")
                except Exception:
                    pass
            return

        log_entry = {
            "text": text,
            "type": msg_type or "info",
            "timestamp": time.strftime("%H:%M:%S"),
        }
        with self._lock:
            self._logs.append(log_entry)

        if self._window:
            try:
                js_str = json.dumps(log_entry)
                self._window.evaluate_js(f"window.onLogReceived && window.onLogReceived({js_str});")
            except Exception:
                pass

    @staticmethod
    def _selected_mods() -> List[str]:
        mods_shared.scan_mods()
        selected: List[str] = []
        for mod in mods_shared.mods_with_order:
            mod_path = mods_shared.get_mod_path(mod)
            cfg = manifest_utils.get_mod(mod_path) if os.path.isdir(mod_path) else {}
            if mods_shared.get_state(mod) or bool(cfg.get("always", False)):
                selected.append(mod)
        return selected

    def get_patch_preview(self) -> Dict[str, Any]:
        selected = self._selected_mods()
        conflicts = mod_library.analyze_conflicts(selected)
        return {
            "selected_mods": [{"id": mod, "name": mod_library.display_name(mod)} for mod in selected],
            "counts": mod_library.conflict_counts(conflicts),
            "estimated_entries": mod_library.estimate_entry_count(selected),
            "compatibility_rules": mod_compat.active_rules(selected),
            "planned_resource_actions": mod_compat.planned_resource_actions(selected),
            "conflicts": conflicts,
        }

    def get_restore_points(self) -> List[Dict[str, Any]]:
        points = []
        for item in backup_manager.list_restore_points():
            selected_mods = item.get("selected_mods")
            points.append(
                {
                    "id": item.get("id"),
                    "created": item.get("created", ""),
                    "completed": item.get("completed", ""),
                    "status": item.get("status", ""),
                    "reason": item.get("reason", ""),
                    "selected_mod_count": len(selected_mods) if isinstance(selected_mods, list) else 0,
                }
            )
        return points

    def restore_point(self, snapshot_id: str) -> Dict[str, Any]:
        if self._is_patching:
            return {"success": False, "error": "Patch operation is running."}

        snapshot_id = str(snapshot_id or "").strip()
        point = next((item for item in backup_manager.list_restore_points() if item.get("id") == snapshot_id), None)
        if not point:
            return {"success": False, "error": "Restore point not found."}

        try:
            result = backup_manager.restore_restore_point(point["path"], restore_selection=True)
            mods_shared.scan_mods()
            output.add_text(f"Restored backup {snapshot_id}.", msg_type="success")
            return {"success": True, **result}
        except Exception as exc:
            output.add_text(f"Restore failed: {exc}", msg_type="error")
            return {"success": False, "error": str(exc)}

    def start_patch(self) -> Dict[str, Any]:
        if self._is_patching:
            return {"status": "already_running"}

        self._is_patching = True
        output.add_text("Patch started. Preparing selected mods and compatibility checks.")
        if self._window:
            try:
                self._window.evaluate_js("window.onPatchStatusChange && window.onPatchStatusChange(true);")
            except Exception:
                pass

        def run_patch_thread() -> None:
            try:
                patch.patcher()
            except Exception as e:
                output.add_text(f"Patch failed: {e}", msg_type="error")
            finally:
                self._is_patching = False
                if self._window:
                    try:
                        self._window.evaluate_js("window.onPatchStatusChange && window.onPatchStatusChange(false);")
                    except Exception:
                        pass

        threading.Thread(target=run_patch_thread, daemon=True).start()
        return {"status": "started"}

    def start_uninstall(self, remove_everything: bool = False) -> Dict[str, Any]:
        if self._is_patching:
            return {"status": "already_running"}

        self._is_patching = True
        if self._window:
            try:
                self._window.evaluate_js("window.onPatchStatusChange && window.onPatchStatusChange(true);")
            except Exception:
                pass

        def run_uninstall_thread() -> None:
            try:
                if remove_everything:
                    patch.unins.wipe()
                else:
                    patch.unins.uninstall()
            except Exception as e:
                output.add_text(f"Uninstall failed: {e}", msg_type="error")
            finally:
                self._is_patching = False
                if self._window:
                    try:
                        self._window.evaluate_js("window.onPatchStatusChange && window.onPatchStatusChange(false);")
                    except Exception:
                        pass

        threading.Thread(target=run_uninstall_thread, daemon=True).start()
        return {"status": "started"}

    def is_patching(self) -> bool:
        return self._is_patching

    def get_logs(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._logs)

    def clear_logs(self) -> bool:
        with self._lock:
            self._logs.clear()
        return True
