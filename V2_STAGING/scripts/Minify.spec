# -*- mode: python ; coding: utf-8 -*-
import glob
import os
import platform
import sys
import sysconfig

from PyInstaller.utils.hooks import collect_submodules


# Import version utility to generate metadata files
sys.path.append(os.path.abspath(SPECPATH))
try:
    import version_util

    if platform.system() == "Windows":
        version_util.generate_metadata()
except ImportError:
    print("Warning: version_util not found, skipping metadata generation")
except Exception as e:
    print(f"Error generating metadata: {e}")

# PyInstaller's Windows dynamic-library discovery first imports every collected
# package in an isolated helper process to observe PATH/add_dll_directory side
# effects. On hosted GitHub Windows runners that heuristic can block forever
# before the actual binary dependency scan starts. The v2 dependency set is
# collected by PyInstaller hooks, so CI skips only that import heuristic while
# retaining the normal PE dependency analysis.
try:
    from pyinstaller_guard import install_windows_ci_guard

    install_windows_ci_guard()
except Exception as e:
    print(f"Warning: PyInstaller CI guard could not be installed: {e}")

# v2 loads mod lifecycle scripts dynamically at runtime. Those scripts are not
# visible to PyInstaller's normal import graph, so keep the rc7 DearPyGui
# runtime available for legacy/user mods such as Transparent HUD.
legacy_script_hiddenimports = ["dearpygui.dearpygui"]
try:
    legacy_script_hiddenimports.extend(collect_submodules("dearpygui"))
except Exception as e:
    print(f"Warning: DearPyGui legacy-script imports could not be collected: {e}")

binaries = []
if platform.system() != "Windows":
    lib_dir = sysconfig.get_config_var("LIBDIR")
    if lib_dir and os.path.isdir(lib_dir):
        for pattern in ("libtcl*.so*", "libtk*.so*"):
            binaries.extend((path, ".") for path in glob.glob(os.path.join(lib_dir, pattern)))

datas = [
    (os.path.abspath(os.path.join(SPECPATH, "../Minify/bin")), "bin"),
    (os.path.abspath(os.path.join(SPECPATH, "../Minify/locales")), "locales"),
    (os.path.abspath(os.path.join(SPECPATH, "../Minify/ui/web/dist")), "ui"),
    (os.path.abspath(os.path.join(SPECPATH, "../Minify/ui/web/src/app.css")), "ui"),
]

a = Analysis(
    ["../Minify/__main__.py"],
    pathex=["../Minify"],
    binaries=binaries,
    datas=datas,
    excludes=["plugins"],
    hiddenimports=["tkinter", "core.plugin_sdk", *legacy_script_hiddenimports],
)

if not any(str(entry[0]).startswith("dearpygui") for entry in a.pure):
    raise RuntimeError("DearPyGui legacy-script compatibility modules were not bundled")
if not any("_dearpygui" in str(entry[0]).casefold() for entry in a.binaries):
    raise RuntimeError("DearPyGui native extension was not bundled")

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Minify",
    console=False,
    icon=["..\\Minify\\bin\\images\\favicon.ico"],
    version="ffi_main.txt" if os.path.exists("ffi_main.txt") else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="Minify",
)

try:
    os.remove("ffi_main.txt")
except:
    pass
