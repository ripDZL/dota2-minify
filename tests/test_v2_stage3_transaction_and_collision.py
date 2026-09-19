from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"


def test_v2_stage3_backup_and_collision_modules_are_present():
    backup = (STAGE / "core" / "backup_manager.py").read_text(encoding="utf-8")
    compat = (STAGE / "core" / "mod_compat.py").read_text(encoding="utf-8")
    library = (STAGE / "core" / "mod_library.py").read_text(encoding="utf-8")

    for token in (
        "def create_restore_point(",
        "def restore_restore_point(",
        "def mark_success(",
        "def mark_rolled_back(",
        "MAX_BACKUPS = 10",
        "security.confined_destination",
    ):
        assert token in backup

    for token in (
        'DARK_TERRAIN_DEFERRED = "materials/dev/deferred_post_process.vmat_c"',
        "def active_dark_terrain_rule(",
        "def exclusions_for_mod(",
        "def copy_standard_files(",
        "def validate_generated_output(",
    ):
        assert token in compat

    for token in (
        'CONTENT_INDEX_FILE = "mod-content-index.json"',
        'COLLISION_REPORT_FILE = "compatibility-report.json"',
        "def fingerprint_entry(",
        "def index_contents(",
        "def analyze_conflicts(",
        "def build_collision_report(",
        "def write_collision_report(",
    ):
        assert token in library


def test_v2_stage3_patch_pipeline_is_transactional_and_collision_aware():
    source = (STAGE / "patch" / "__init__.py").read_text(encoding="utf-8")
    for token in (
        "backup_manager.create_restore_point(",
        "mod_library.analyze_conflicts(",
        "mod_library.write_collision_report(",
        "mod_compat.active_rules(",
        "mod_compat.copy_standard_files(",
        "exclude_paths=mod_compat.exclusions_for_mod(",
        "mod_compat.validate_generated_output(",
        "backup_manager.mark_success(",
        "backup_manager.restore_restore_point(",
        "backup_manager.mark_rolled_back(",
    ):
        assert token in source

    assert "patch_completed = False" in source
    assert "_rollback_failed_patch(restore_point if not patch_completed else None" in source


def test_v2_stage3_vpk_dump_supports_compatibility_exclusions():
    source = (STAGE / "patch" / "vpk_utils.py").read_text(encoding="utf-8")
    assert "def dump(vpk_obj, output_dir, check_exists=True, exclude_paths=None):" in source
    assert "security.confined_destination(output_dir, filepath)" in source
    assert "if clean_path.casefold() in excluded:" in source


def test_v2_stage3_patch_service_exposes_preflight_and_restore_points():
    service = (STAGE / "ui" / "services" / "patch_service.py").read_text(encoding="utf-8")
    app = (STAGE / "ui" / "app.py").read_text(encoding="utf-8")
    global_types = (STAGE / "ui" / "web" / "src" / "global.d.ts").read_text(encoding="utf-8")

    for token in (
        "def get_patch_preview(",
        "mod_library.analyze_conflicts(selected)",
        "mod_compat.active_rules(selected)",
        "def get_restore_points(",
        "def restore_point(",
        "backup_manager.restore_restore_point(",
    ):
        assert token in service

    for token in (
        "def get_patch_preview(",
        "def get_restore_points(",
        "def restore_point(",
    ):
        assert token in app

    assert "get_patch_preview?:" in global_types
    assert "get_restore_points?:" in global_types
    assert "restore_point?:" in global_types


def test_v2_stage3_svelte_has_review_and_restore_surfaces():
    app = (STAGE / "ui" / "web" / "src" / "App.svelte").read_text(encoding="utf-8")
    header = (STAGE / "ui" / "web" / "src" / "lib" / "components" / "Header.svelte").read_text(encoding="utf-8")
    review = (
        STAGE / "ui" / "web" / "src" / "lib" / "components" / "PatchReviewModal.svelte"
    ).read_text(encoding="utf-8")
    restore = (
        STAGE / "ui" / "web" / "src" / "lib" / "components" / "RestoreModal.svelte"
    ).read_text(encoding="utf-8")

    assert "openPatchReview" in app
    assert "get_patch_preview" in app
    assert "openRestoreManager" in app
    assert "get_restore_points" in app
    assert "restore_point" in app
    assert "onRestoreClick={openRestoreManager}" in app

    assert "export let onRestoreClick" in header
    assert "Restore" in header

    for token in ("Patch review", "Automatic compatibility", "Resource overlaps", "Create restore point & patch"):
        assert token in review
    for token in ("Restore points", "Restore selected", "Selected mods:"):
        assert token in restore
