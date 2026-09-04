from pathlib import Path


PATCHER = Path("Minify/patch/__init__.py")


def _source() -> str:
    return PATCHER.read_text(encoding="utf-8")


def test_nested_mod_paths_use_discovered_ids():
    source = _source()
    assert "mods_shared.get_mod_path(folder)" in source
    assert "mods_shared.get_mod_path(mod_name)" in source
    assert "mods_shared.resolve_mod_reference(dependency, relative_to=dependant)" in source
    assert "mods_shared.resolve_mod_reference(conflicting_mod, relative_to=conflict_mod)" in source


def test_patch_creates_transactional_restore_point():
    source = _source()
    assert "backup_manager.create_restore_point(" in source
    assert 'reason="pre-patch"' in source
    assert "backup_manager.mark_success(restore_point)" in source


def test_patch_rolls_back_managed_output_on_failure():
    source = _source()
    assert "backup_manager.restore_restore_point(restore_point, restore_selection=False)" in source
    assert "backup_manager.mark_rolled_back(restore_point, str(error))" in source
    assert "patch_completed = False" in source


def test_patch_runs_conflict_preflight_and_report():
    source = _source()
    assert "mod_library.analyze_conflicts(selected_for_backup)" in source
    assert "mod_library.write_collision_report(selected_for_backup, conflicts)" in source
    assert "mod_library.conflict_counts(conflicts)" in source


def test_standard_and_vpk_paths_use_compatibility_layer():
    source = _source()
    assert "mod_compat.copy_standard_files(" in source
    assert "exclude_paths=mod_compat.exclusions_for_mod(mod_name, selected_for_backup)" in source


def test_generated_output_is_compatibility_validated():
    source = _source()
    assert "mod_compat.validate_generated_output(" in source
    assert "Compatibility validation passed: Dark Terrain yields deferred post-process safely." in source


def test_normal_patch_never_adds_minify_prelaunch_command():
    source = _source()
    assert "steam.remove_minify_prelaunch_from_launch_options(check_only=True)" in source
    assert "steam.remove_minify_prelaunch_from_launch_options()" in source
    assert "steam.add_prelaunch_to_launch_options()" not in source
    assert "steam.add_prelaunch_to_launch_options(check_only=True)" not in source


def test_patch_reports_ui_status_and_failures():
    source = _source()
    assert '_checkboxes.set_status("Restore point created. Patching...", "working")' in source
    assert '_checkboxes.set_status("Patch completed successfully.", "success")' in source
    assert "_checkboxes.report_patch_error(error_details + rollback_message)" in source
