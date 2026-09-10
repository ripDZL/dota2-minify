import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

import vpk
from core import base, constants, fs, log, utils


def process(blacklist_txt, folder, blank_file_extensions):
    with utils.open_utf8(blacklist_txt) as file:
        lines = file.readlines()
        blacklist_data = []
        blacklist_data_exclusions = set()
        blank_exts = tuple(blank_file_extensions)

        for index, line in enumerate(lines):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            elif line.startswith((">>", "**")):
                blacklist_data.extend(process_dir(index, line, folder))

            elif line.startswith("*-"):
                blacklist_data_exclusions.update(process_dir(index, line, folder))

            elif line.startswith("--"):
                blacklist_data_exclusions.add(line[2:])

            else:
                if line.endswith(blank_exts):
                    blacklist_data.append(line)
                else:
                    log.write_warning(
                        f"[Invalid Extension] '{line}' in 'mods/{folder}/blacklist.txt' [line: {index + 1}] does not end in one of the valid extensions -> {blank_file_extensions}"
                    )

    blacklist_data_set = set(blacklist_data)
    for exclusion in blacklist_data_exclusions:
        if exclusion not in blacklist_data_set:
            print(
                f"[Unnecessary Exclusion] '{exclusion}' in '{folder}' is not necessary, the mod doesn't include this file."
            )

    blacklist_data = [item for item in blacklist_data if item not in blacklist_data_exclusions]

    def copy_blank_file(line):
        line = line.strip()
        path, extension = os.path.splitext(line)

        fs.create_dirs(os.path.join(constants.minify_dota_compile_output_path, os.path.dirname(path)))

        try:
            shutil.copy(
                os.path.join(base.blank_files_dir, f"blank{extension}"),
                os.path.join(
                    constants.minify_dota_compile_output_path,
                    path + extension,
                ),
            )
        except FileNotFoundError:
            log.write_warning(
                f"[Invalid Extension] '{line}' in 'mods/{os.path.basename(folder)}/blacklist.txt' does not end in one of the valid extensions -> {blank_file_extensions}"
            )

    with ThreadPoolExecutor() as executor:
        executor.map(copy_blank_file, blacklist_data)

    rerl_file = os.path.join(os.path.dirname(blacklist_txt), "rerl.json")
    if os.path.isfile(rerl_file):
        try:
            from patch import rerl_processor

            rerl_processor.process(rerl_file, folder, vpk.open(constants.dota_game_pak_path))
        except Exception as exc:
            log.write_warning(f"Failed to process rerl.json for {folder}: {exc}")


def process_dir(index, line, folder):
    data = []

    line = line[2:] if line.startswith("**") or line.startswith("*-") else line
    line = line + "/" if line.startswith(">>") else line
    line = line[2:] if line.startswith(">>") else line

    lines = subprocess.run(
        [
            constants.rg_exec_path,
            "--no-filename",
            "--no-line-number",
            "--color=never",
            line,
            os.path.join(base.bin_dir, "gamepakcontents.txt"),
        ],
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if base.is_win else 0,
    )
    data = lines.stdout.splitlines()

    if not data:
        log.write_warning(
            f"[Directory Not Found] Could not find '{line}' in pak01_dir.vpk -> mods/{folder}/blacklist.txt [line: {index + 1}]"
        )

    return data
