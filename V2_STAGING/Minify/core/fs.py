"Filesystem access"

import os
import shlex
import shutil
import stat
import subprocess
import tempfile
import time
from collections.abc import Callable
from typing import Optional

import requests

from core import base, log, output, security, utils


def open_thing(path: str, args: str = ""):
    "Opens files or directories in their regsitered applications"

    try:
        # If args are provided and target is executable, prefer launching directly
        if args:
            if base.is_win:
                os.startfile(path, arguments=args)
                return
            # POSIX: launch executable directly when possible
            if os.access(path, os.X_OK) and os.path.isfile(path):
                cmd = [path] + shlex.split(args)
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            # Non-executables with args: fall back to opening container directory
            path = os.path.dirname(path) or "."

        # No args path open
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
                # Reveal the file in Finder to avoid missing-app association errors
                subprocess.run(["open", "-R", path])
            else:
                subprocess.run(["xdg-open", path])
    except FileNotFoundError:
        output.add_text("&open_thing_fail", path, msg_type="error")


def move_path(src: str, dst: str):
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


def remove_path(*paths: str):
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


def create_dirs(*paths: str):
    """
    Recursively creates directories (like mkdir -p).
    Supports multiple arguments and avoids crashing on empty paths.
    """
    for path in paths:
        if path:
            os.makedirs(path, exist_ok=True)


def backup_directory(source: str, backup: str):
    """Copy entire contents of source into backup. No-op if backup already exists."""
    if os.path.exists(backup):
        return
    create_dirs(backup)
    for name in os.listdir(source):
        move_path(os.path.join(source, name), os.path.join(backup, name))


def restore_directory(source: str, backup: str):
    """Restore contents from backup into source, then remove backup."""
    if not os.path.exists(backup):
        return
    for name in os.listdir(source):
        remove_path(os.path.join(source, name))
    for name in os.listdir(backup):
        move_path(os.path.join(backup, name), os.path.join(source, name))
    remove_path(backup)
    parent = os.path.dirname(backup)
    if os.path.exists(parent) and not os.listdir(parent):
        remove_path(parent)


def _validated_stream_response(
    url: str,
    *,
    url_validator: Callable[[str], None],
    timeout: tuple[int, int],
    max_redirects: int,
):
    """Open a streamed response while validating every redirect target."""
    current = str(url)
    redirect_codes = {301, 302, 303, 307, 308}
    for redirect_count in range(max_redirects + 1):
        url_validator(current)
        response = requests.get(current, stream=True, timeout=timeout, allow_redirects=False)
        if response.status_code not in redirect_codes:
            try:
                response.raise_for_status()
                url_validator(str(getattr(response, "url", "") or current))
                return response
            except Exception:
                response.close()
                raise

        location = response.headers.get("location")
        response.close()
        if not location:
            raise ValueError("Download redirect is missing a Location header.")
        if redirect_count >= max_redirects:
            raise ValueError(f"Download exceeded the {max_redirects}-redirect safety limit.")
        current = requests.compat.urljoin(current, location)

    raise ValueError("Download redirect validation failed.")


def download_file(
    url: str,
    target_path: str,
    progress_tag: Optional[str] = None,
    name: Optional[str] = None,
    emit_progress: bool = True,
    task_id: Optional[str] = None,
    max_bytes: int | None = security.ARCHIVE_MAX_FILE_BYTES,
    url_validator: Callable[[str], None] | None = None,
    max_redirects: int = 5,
) -> bool:
    """Download atomically with request timeouts, redirect validation, and a byte cap."""
    response = None
    temporary = None
    file_name = name or os.path.basename(target_path)
    task_id = task_id or target_path

    def emit(downloaded: int, total: int, status: str, error: str | None = None) -> None:
        if not emit_progress or not hasattr(output, "emit_download_progress"):
            return
        output.emit_download_progress(task_id, file_name, downloaded, total, status, error=error)

    try:
        if max_bytes is not None and max_bytes < 1:
            raise ValueError("max_bytes must be positive or None.")
        if max_redirects < 0 or max_redirects > 20:
            raise ValueError("max_redirects must be between 0 and 20.")

        timeout = (10, 60)
        if url_validator is None:
            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()
        else:
            response = _validated_stream_response(
                url,
                url_validator=url_validator,
                timeout=timeout,
                max_redirects=max_redirects,
            )

        try:
            total_size = int(response.headers.get("content-length", 0) or 0)
        except (TypeError, ValueError):
            total_size = 0
        if max_bytes is not None and total_size > max_bytes:
            raise ValueError(f"Download exceeds the {max_bytes}-byte safety limit.")

        parent = os.path.dirname(os.path.abspath(target_path)) or os.getcwd()
        os.makedirs(parent, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".minify-download-", dir=parent)

        downloaded = 0
        last_report_time = 0.0
        emit(0, total_size, "downloading")
        with os.fdopen(fd, "wb") as file:
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                downloaded += len(chunk)
                if max_bytes is not None and downloaded > max_bytes:
                    raise ValueError(f"Download exceeds the {max_bytes}-byte safety limit.")
                file.write(chunk)

                now = time.time()
                if now - last_report_time >= 0.1:
                    emit(downloaded, total_size, "downloading")
                    if progress_tag:
                        downloaded_mb = downloaded / (1024 * 1024)
                        total_size_mb = total_size / (1024 * 1024)
                        if total_size:
                            output.add_text(f"Downloading: {downloaded_mb:.2f}/{total_size_mb:.2f} MB")
                        else:
                            output.add_text(f"Downloading: {downloaded_mb:.2f} MB")
                    last_report_time = now

        os.replace(temporary, target_path)
        temporary = None
        emit(downloaded, total_size, "finished")
        return True
    except Exception as exc:
        if temporary:
            try:
                os.remove(temporary)
            except FileNotFoundError:
                pass
        emit(0, 0, "error", str(exc))
        output.add_text(f"Failed to open {target_path}: {exc}", msg_type="error")
        return False
    finally:
        if response is not None:
            try:
                response.close()
            except Exception:
                pass


def extract_archive(archive_path: str, extract_dir: str = ".", target_file: Optional[str] = None) -> bool:
    """Extract ZIP/tar.gz archives with shared traversal, symlink, and size limits."""
    try:
        security.safe_extract_archive(archive_path, extract_dir, target_file=target_file)
        return True
    except Exception as exc:
        output.add_text(f"Extraction failed: {exc}", msg_type="error")
        return False

def get_file_type(path: str) -> Optional[str]:
    """
    Identifies the file type. It first checks magic bytes (e.g., '.png', '.jpg', '.webm'),
    and falls back to extracting the extension from the first dot in the filename if no known magic bytes are found.
    """
    # can be extended by just handing it to a module
    with utils.try_pass():
        if not os.path.exists(path):
            return None

        with open(path, "rb") as f:
            header = f.read(16)

            # PNG: 89 50 4E 47 0D 0A 1A 0A
            if header.startswith(b"\x89PNG\r\n\x1a\n"):
                return ".png"

            # JPEG: FF D8 FF (Start of Image + specific marker)
            if header.startswith(b"\xff\xd8\xff"):
                return ".jpg"

            # WEBP: RIFF....WEBP
            if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
                return ".webp"

            # WEBM/MKV: 1A 45 DF A3 (EBML)
            if header.startswith(b"\x1a\x45\xdf\xa3"):
                return ".webm"

            # MP4: ....ftyp
            if header[4:8] == b"ftyp":
                return ".mp4"

            # GIF
            if header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
                return ".gif"

    # Fallback: return extension from the first dot or the filename itself if no dot exists
    basename = os.path.basename(path)
    dot_index = basename.find(".")
    if dot_index != -1:
        return basename[dot_index:]

    return basename
