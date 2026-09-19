from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"


def _read(relative: str) -> str:
    return (STAGE / relative).read_text(encoding="utf-8")


def test_v2_stage1_staged_python_sources_compile():
    for path in STAGE.rglob("*.py"):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")


def test_v2_d2pfx_data_uses_shared_bounded_network_and_cache_guards():
    source = _read("plugins/d2pfx/data.py")
    for token in (
        "security.validate_public_https_url",
        "security.bounded_zlib_decompress",
        "security.D2PFX_MAX_MANIFEST_BYTES",
        "tempfile.mkstemp",
        "os.replace(temporary, local_path)",
        "security.safe_relative_path",
        "security.confined_destination",
        "security.read_bounded_regular_file",
    ):
        assert token in source
    assert "gzip.GzipFile" not in source
    assert "response.content" not in source


def test_v2_d2pfx_install_is_staged_confined_and_atomically_published():
    source = _read("plugins/d2pfx/api.py")
    for token in (
        "security.confined_destination(base.mods_dir, target_folder)",
        "security.safe_download_filename",
        'tempfile.mkdtemp(prefix=".d2pfx-install-", dir=base.mods_dir)',
        "fs.extract_archive(mod_dest, install_dir)",
        "os.replace(install_dir, target_dir)",
        "if os.path.lexists(target_dir):",
    ):
        assert token in source
    assert "fs.create_dirs(target_dir)" not in source
    assert "os.path.basename(mod_url)" not in source


def test_v2_d2pfx_cursor_port_rejects_symlinks_and_uses_atomic_regular_file_copy():
    source = _read("plugins/d2pfx/build_hook.py")
    for token in (
        "followlinks=False",
        "follow_symlinks=False",
        "CURSOR_MAX_FILES = 512",
        "CURSOR_MAX_FILE_BYTES",
        "CURSOR_MAX_TOTAL_BYTES",
        "security.confined_destination",
        "tempfile.mkstemp",
        "os.replace(temporary, destination)",
    ):
        assert token in source
    assert "shutil.copy2" not in source


def test_v2_remap_port_validates_rule_shape_and_confines_all_write_paths():
    source = _read("patch/remap_processor.py")
    for token in (
        "def _validate_rules",
        "REMAP_MAX_RULES",
        "REMAP_MAX_REDIRECTS_PER_RULE",
        "security.safe_relative_path",
        "security.confined_destination",
        "REMAP_MAX_RESOURCE_BYTES",
        "REMAP_MAX_SOURCE_CHARS",
    ):
        assert token in source
    assert '.lstrip("/")' not in source
    assert "os.path.join(constants.minify_dota_compile_output_path, clean_path)" not in source


def test_v2_update_requires_digest_and_workshop_install_is_transactional():
    source = _read("ui/app.py")
    for token in (
        "def _validate_github_https_url",
        "def _fetch_bounded_json",
        "def _verify_sha256",
        "def perform_update(self, url: str, sha256: str | None = None)",
        "The update asset is missing its GitHub SHA-256 digest.",
        "max_bytes=UPDATE_MAX_BYTES",
        "url_validator=_validate_github_https_url",
        "expected_digest = str(chosen[\"digest\"])",
        'tempfile.mkdtemp(prefix=".minify-rescomp-stage-", dir=parent)',
        'tempfile.mkdtemp(prefix=".minify-rescomp-backup-", dir=parent)',
        "os.replace(payload_dir, target_dir)",
        "os.replace(backup_dir, target_dir)",
    ):
        assert token in source
    assert "response.json()" not in source
    assert "extractall(" not in source


def test_v2_web_updater_propagates_github_asset_digest_to_backend():
    updater = _read("ui/web/src/lib/updater.ts")
    types = _read("ui/web/src/lib/types.ts")
    modal = _read("ui/web/src/lib/components/UpdateModal.svelte")
    global_types = _read("ui/web/src/global.d.ts")

    assert 'if (/^sha256:[0-9a-f]{64}$/i.test(digest))' in updater
    assert "downloadSha256: downloadSha256 || undefined" in updater
    assert "downloadSha256?: string;" in types
    assert "api.perform_update(url, updateInfo.downloadSha256 || null)" in modal
    assert "perform_update: (url: string, sha256?: string | null)" in global_types
