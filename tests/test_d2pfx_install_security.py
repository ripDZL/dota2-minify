from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_SOURCE = (ROOT / "Minify" / "browsers" / "d2pfx" / "ui.py").read_text(encoding="utf-8")


def _install_block():
    start = UI_SOURCE.index("    def install_mod(self, mod):")
    end = UI_SOURCE.index("    def uninstall_mod(self, mod):", start)
    return UI_SOURCE[start:end]


def test_d2pfx_browser_preview_cache_uses_validated_bounded_downloads():
    assert "fs.download_file(url, local_path)" not in UI_SOURCE
    assert "fs.download_file(root_url, local_path)" not in UI_SOURCE
    assert "self.data_manager.download_file(url, local_path, max_bytes=D2PFX_PREVIEW_MAX_BYTES)" in UI_SOURCE
    assert UI_SOURCE.count("self.data_manager.download_file(") >= 2
    assert "root_url, local_path, max_bytes=D2PFX_PREVIEW_MAX_BYTES" in UI_SOURCE


def test_d2pfx_install_uses_staging_and_atomic_publication():
    block = _install_block()
    assert 'tempfile.mkdtemp(prefix=".d2pfx-install-", dir=base.mods_dir)' in block
    assert 'install_dir = os.path.join(staging_root, "payload")' in block
    assert "os.replace(install_dir, target_dir)" in block
    assert "if staging_root:" in block
    assert "fs.remove_path(staging_root)" in block


def test_d2pfx_install_derives_safe_filename_from_url_path():
    block = _install_block()
    assert 'safe_download_filename(mod_url, allowed_extensions={".vpk", ".zip"})' in block
    assert "os.path.basename(mod_url)" not in block


def test_d2pfx_install_extracts_and_writes_metadata_only_in_staging():
    block = _install_block()
    assert "fs.extract_archive(mod_dest, install_dir)" in block
    assert 'os.path.join(install_dir, "manifest.json")' in block
    assert 'os.path.join(install_dir, "notes.md")' in block
    assert 'preview_dest = os.path.join(install_dir, "preview.jpg")' in block
    assert "max_bytes=D2PFX_PREVIEW_MAX_BYTES" in block


def test_d2pfx_install_refuses_existing_target_before_and_during_publish():
    block = _install_block()
    assert block.count("if os.path.lexists(target_dir):") >= 2
