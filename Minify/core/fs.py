"Filesystem access"

import os
import shlex
import shutil
import stat
import subprocess
import tempfile
import tarfile
import time
import zipfile
from typing import Optional

import dearpygui.dearpygui as dpg
import requests

from core import base, log, output, security, utils


def open_thing(path: str, args: str = "") -> None:
    "Opens files or directories in their regsitered applications"

    try:
        if args:
            if base.is_win:
                os.startfile(path, arguments=args)
                return
            if os.access(path, os.X_OK) and os.path.isfile(path):
                cmd = [path] + shlex.split(args)
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            path = os.path.dirname(path) or "."

        if os.path.isdir(path):
            if base.is_win:
                os.startfile(path)
            elif base.is_mac:
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        else:
            if base.is_win:
                os.startfile(path)
            elif base.is_mac:
                subprocess.run(["open", "-R", path])
            else:
                subprocess.run(["xdg-open", path])
    except FileNotFoundError:
        output.add_text("&open_thing_fail", path, msg_type="error")


def move_path(src: str, dst: str) -> Optional[None]:
    "Superset of `shutil.move`, `os.rename` to handle permissions for moving and renaming."
    try:
        shutil.move(src, dst)
    except PermissionError:
        try:
            paths_to_chmod = []
            if os.path.exists(src):
                paths_to_chmod.append(src)
            if os.path.exists(dst):
                paths_to_chmod.append(dst)

            for path in paths_to_chmod:
                if os.path.isdir(path):
                    for root, _, filenames in os.walk(path):
                        current_dir_mode = os.stat(root).st_mode
                        os.chmod(root, current_dir_mode | stat.S_IWUSR)

                        for filename in filenames:
                            filepath = os.path.join(root, filename)
                            current_file_mode = os.stat(filepath).st_mode
                            os.chmod(filepath, current_file_mode | stat.S_IWUSR)
                else:
                    current_file_mode = os.stat(path).st_mode
                    os.chmod(path, current_file_mode | stat.S_IWUSR)

            return move_path(src, dst)
        except Exception:
            log.write_warning()
    except FileNotFoundError:
        print(f"Skipped move of: {src} (not found)")


def remove_path(*paths: str) -> Optional[None]:
    "Superset of `shutil.rmtree` & `os.remove` to handle permissions. Takes in list of paths."
    try:
        for path in paths:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except FileNotFoundError:
                print(f"Skipped deletion of: {path}")

    except PermissionError:
        try:
            for path in paths:
                if os.path.isdir(path):
                    for root, _, filenames in os.walk(path):
                        current_dir_mode = os.stat(root).st_mode
                        os.chmod(root, current_dir_mode | stat.S_IWUSR)

                        for filename in filenames:
                            filepath = os.path.join(root, filename)
                            current_file_mode = os.stat(filepath).st_mode
                            os.chmod(filepath, current_file_mode | stat.S_IWUSR)
                else:
                    current_file_mode = os.stat(path).st_mode
                    os.chmod(path, current_file_mode | stat.S_IWUSR)

            return remove_path(*paths)
        except Exception:
            log.write_warning()


def create_dirs(*paths: str) -> None:
    """
    Recursively creates directories (like mkdir -p).
    Supports multiple arguments and avoids crashing on empty paths.
    """
    for path in paths:
        if path:
            os.makedirs(path, exist_ok=True)


def backup_directory(source: str, backup: str) -> None:
    """Copy entire contents of source into backup. No-op if backup already exists."""
    if os.path.exists(backup):
        return
    create_dirs(backup)
    for name in os.listdir(source):
        move_path(os.path.join(source, name), os.path.join(backup, name))


def restore_directory(source: str, backup: str) -> None:
    """Restore contents from backup into source, then remove backup."""
    if not os.path.exists(backup):
        return
    for name in os.listdir(source):
        remove_path(os.path.join(source, name))
    for name in os.listdir(backup):
        move_path(os.path.join(backup, name), os.path.join(source, name))
    remove_path(backup)


def download_file(
    url: str,
    target_path: str,
    progress_tag: Optional[str] = None,
    max_bytes: int | None = security.ARCHIVE_MAX_FILE_BYTES,
) -> bool:
    """Download to a temporary file with bounded size and request timeouts."""
    response = None
    temporary = None
    try:
        if max_bytes is not None and max_bytes < 1:
            raise ValueError("max_bytes must be positive or None")

        response = requests.get(url, stream=True, timeout=(10, 60))
        response.raise_for_status()
        try:
            total_size = int(response.headers.get("content-length", 0) or 0)
        except (TypeError, ValueError):
            total_size = 0
        if max_bytes is not None and total_size > max_bytes:
            raise ValueError(f"Download exceeds the {max_bytes}-byte safety limit.")

        block_size = 8192
        downloaded = 0
        last_report_time = 0
        parent = os.path.dirname(os.path.abspath(target_path)) or os.getcwd()
        os.makedirs(parent, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".minify-download-", dir=parent)

        with os.fdopen(fd, "wb") as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if not chunk:
                    continue
                downloaded += len(chunk)
                if max_bytes is not None and downloaded > max_bytes:
                    raise ValueError(f"Download exceeds the {max_bytes}-byte safety limit.")
                f.write(chunk)
                if progress_tag:
                    current_time = time.time()
                    if current_time - last_report_time >= 0.1:
                        downloaded_mb = downloaded / (1024 * 1024)
                        total_size_mb = total_size / (1024 * 1024)
                        if total_size > 0:
                            dpg.set_value(
                                progress_tag,
                                f"Downloading: {downloaded_mb:.2f}/{total_size_mb:.2f} MB",
                            )
                        else:
                            dpg.set_value(progress_tag, f"Downloading: {downloaded_mb:.2f} MB")
                        last_report_time = current_time

        os.replace(temporary, target_path)
        temporary = None

        if progress_tag:
            downloaded_mb = downloaded / (1024 * 1024)
            total_size_mb = total_size / (1024 * 1024)
            if total_size > 0:
                dpg.set_value(progress_tag, f"Downloading: {downloaded_mb:.2f}/{total_size_mb:.2f} MB")
            else:
                dpg.set_value(progress_tag, f"Downloading: {downloaded_mb:.2f} MB")
        return True
    except Exception as e:
        if temporary:
            try:
                os.remove(temporary)
            except FileNotFoundError:
                pass
        output.add_text(f"Failed to open {target_path}: {e}", msg_type="error")
        return False
    finally:
        if response is not None:
            with utils.try_pass():
                response.close()


def extract_archive(archive_path: str, extract_dir: str = ".", target_file: Optional[str] = None) -> bool:
    """Extract ZIP/tar.gz archives using shared path/size/symlink protections."""
    try:
        security.safe_extract_archive(archive_path, extract_dir, target_file=target_file)
        return True
    except Exception as e:
        output.add_text(f"Extraction failed: {e}", msg_type="error")
        return False


def get_file_type(path: str) -> Optional[str]:
    """
    Identifies the file type. It first checks magic bytes (e.g., '.png', '.jpg', '.webm'),
    and falls back to extracting the extension from the first dot in the filename if no known magic bytes are found.
    """
    with utils.try_pass():
        if not os.path.exists(path):
            return None

        with open(path, "rb") as f:
            header = f.read(16)

            if header.startswith(b"\x89PNG\r\n\x1a\n"):
                return ".png"

            if header.startswith(b"\xff\xd8\xff"):
                return ".jpg"

            if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
                return ".webp"

            if header.startswith(b"\x1a\x45\xdf\xa3"):
                return ".webm"

            if header[4:8] == b"ftyp":
                return ".mp4"

            if header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
                return ".gif"

    basename = os.path.basename(path)
    dot_index = basename.find(".")
    if dot_index != -1:
        return basename[dot_index:]

    return basename
