from pathlib import Path


PATH = Path("Minify/browsers/d2pfx/ui.py")
text = PATH.read_text(encoding="utf-8")

if "import tempfile\n" not in text:
    anchor = "import threading\n"
    if anchor not in text:
        raise SystemExit("missing threading import anchor")
    text = text.replace(anchor, anchor + "import tempfile\n", 1)

old_import = "from browsers.d2pfx.data import DataManager\n"
new_import = "from browsers.d2pfx.data import D2PFX_PREVIEW_MAX_BYTES, DataManager, safe_download_filename\n"
if old_import in text:
    text = text.replace(old_import, new_import, 1)
elif new_import not in text:
    raise SystemExit("missing DataManager import anchor")

# Preview cache downloads must use the D2PFX network validator and a small image ceiling.
text = text.replace(
    "if not fs.download_file(url, local_path):",
    "if not self.data_manager.download_file(url, local_path, max_bytes=D2PFX_PREVIEW_MAX_BYTES):",
    1,
)
text = text.replace(
    "if not fs.download_file(root_url, local_path):",
    "if not self.data_manager.download_file(root_url, local_path, max_bytes=D2PFX_PREVIEW_MAX_BYTES):",
    1,
)

start = text.index("    def install_mod(self, mod):")
end = text.index("    def uninstall_mod(self, mod):", start)
block = text[start:end]

old_start = '''        def _task():
            try:
                modal_shared.show_progress([f"Installing {name}...", "Downloading mod files..."])
                fs.create_dirs(target_dir)

                # 1. Download Mod File
                mod_dest = os.path.join(target_dir, os.path.basename(mod_url))
'''
new_start = '''        def _task():
            staging_root = None
            try:
                modal_shared.show_progress([f"Installing {name}...", "Downloading mod files..."])
                fs.create_dirs(base.mods_dir)
                if os.path.lexists(target_dir):
                    raise ValueError("A mod directory with this D2PFX name already exists. Refresh the library before installing again.")
                staging_root = tempfile.mkdtemp(prefix=".d2pfx-install-", dir=base.mods_dir)
                install_dir = os.path.join(staging_root, "payload")
                fs.create_dirs(install_dir)

                # 1. Download Mod File
                mod_filename = safe_download_filename(mod_url, allowed_extensions={".vpk", ".zip"})
                mod_dest = os.path.join(install_dir, mod_filename)
'''
if old_start not in block:
    raise SystemExit("missing install task anchor")
block = block.replace(old_start, new_start, 1)

old_extract = "if not fs.extract_archive(mod_dest, target_dir):"
if old_extract not in block:
    raise SystemExit("missing install extraction anchor")
block = block.replace(old_extract, "if not fs.extract_archive(mod_dest, install_dir):", 1)

old_preview_dest = 'preview_dest = os.path.join(target_dir, "preview.jpg")'
if old_preview_dest not in block:
    raise SystemExit("missing preview destination anchor")
block = block.replace(old_preview_dest, 'preview_dest = os.path.join(install_dir, "preview.jpg")', 1)

old_preview_download = "self.data_manager.download_file(preview_url, preview_dest)"
if old_preview_download not in block:
    raise SystemExit("missing preview download anchor")
block = block.replace(
    old_preview_download,
    "self.data_manager.download_file(preview_url, preview_dest, max_bytes=D2PFX_PREVIEW_MAX_BYTES)",
    1,
)

old_manifest = 'config.write_json_file(os.path.join(target_dir, "manifest.json"), modcfg)'
if old_manifest not in block:
    raise SystemExit("missing manifest anchor")
block = block.replace(old_manifest, 'config.write_json_file(os.path.join(install_dir, "manifest.json"), modcfg)', 1)

old_notes = 'with open(os.path.join(target_dir, "notes.md"), "w", encoding="utf-8") as f:'
if old_notes not in block:
    raise SystemExit("missing notes anchor")
block = block.replace(old_notes, 'with open(os.path.join(install_dir, "notes.md"), "w", encoding="utf-8") as f:', 1)

publish_anchor = '''                with open(os.path.join(install_dir, "notes.md"), "w", encoding="utf-8") as f:
                    f.write(notes_content)

                modal_shared.show(
'''
publish_replacement = '''                with open(os.path.join(install_dir, "notes.md"), "w", encoding="utf-8") as f:
                    f.write(notes_content)

                # Publish only after download, extraction, preview, and metadata are complete.
                if os.path.lexists(target_dir):
                    raise ValueError("The D2PFX target directory appeared during installation; refusing to overwrite it.")
                os.replace(install_dir, target_dir)
                fs.remove_path(staging_root)
                staging_root = None

                modal_shared.show(
'''
if publish_anchor not in block:
    raise SystemExit("missing publish anchor")
block = block.replace(publish_anchor, publish_replacement, 1)

old_except = '''            except Exception as e:
                modal_shared.show("Installation Failed", [str(e)], [{"label": "OK"}])
'''
new_except = '''            except Exception as e:
                if staging_root:
                    fs.remove_path(staging_root)
                modal_shared.show("Installation Failed", [str(e)], [{"label": "OK"}])
'''
if old_except not in block:
    raise SystemExit("missing install exception anchor")
block = block.replace(old_except, new_except, 1)

text = text[:start] + block + text[end:]
PATH.write_text(text, encoding="utf-8", newline="\n")
print("D2PFX install hardening applied")
