from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"


def test_v2_profile_service_has_update_import_export_parity():
    service = (STAGE / "ui" / "services" / "mod_service.py").read_text(encoding="utf-8")
    for token in (
        "def update_profile(",
        "def export_profile_bundle(",
        "PROFILE_EXPORT_FORMAT",
        "mod_library.stable_key(mod, calculate_hash=False)",
        "def _profile_identity_indexes(",
        "def _remap_imported_states(",
        "def import_profile_bundle(",
        'base_name = f"{name} (Imported)"',
        "self.apply_profile(applied_name)",
    ):
        assert token in service


def test_v2_profile_file_io_is_bounded_atomic_and_symlink_safe():
    app = (STAGE / "ui" / "app.py").read_text(encoding="utf-8")
    for token in (
        "def export_profiles(",
        'pick_save_file("Export Profiles", "Minify-Profiles.json")',
        'if os.path.lexists(path) and os.path.islink(path):',
        'tempfile.mkstemp(prefix=".minify-profile-export-"',
        "os.replace(temporary, path)",
        "def import_profiles(",
        'pick_file("Import Profiles", ("JSON files (*.json)",))',
        "profiles.read_profile_file(path)",
        "self.mod_service.import_profile_bundle(data)",
    ):
        assert token in app


def test_v2_profile_reads_use_identity_checked_bounded_helper():
    profiles = (STAGE / "core" / "profiles.py").read_text(encoding="utf-8")
    security = (STAGE / "core" / "security.py").read_text(encoding="utf-8")

    assert "def read_profile_file(path: str):" in profiles
    assert "security.read_bounded_regular_file(path, max_bytes=PROFILE_MAX_FILE_BYTES)" in profiles
    assert "def read_bounded_regular_file(path: str, *, max_bytes: int) -> bytes:" in security
    assert "os.stat(path, follow_symlinks=False)" in security
    assert "opened = os.fstat(fd)" in security
    assert "(before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)" in security


def test_v2_profile_ui_exposes_update_import_export_controls():
    grid = (
        STAGE / "ui" / "web" / "src" / "lib" / "components" / "ModGrid.svelte"
    ).read_text(encoding="utf-8")
    global_types = (STAGE / "ui" / "web" / "src" / "global.d.ts").read_text(encoding="utf-8")

    for token in (
        "updateSelectedProfile",
        "importProfiles",
        "exportProfiles",
        ">Update</button>",
        ">Import</button>",
        ">Export</button>",
        "mod ID(s) remapped",
    ):
        assert token in grid

    assert "update_profile?:" in global_types
    assert "import_profiles?:" in global_types
    assert "export_profiles?:" in global_types
