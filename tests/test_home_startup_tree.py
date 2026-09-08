from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "Minify" / "__main__.py").read_text(encoding="utf-8")

# Startup must construct only the final compact Home tree; retired widgets may
# not exist even briefly before runtime layout helpers execute.


def test_retired_home_widgets_are_not_constructed():
    for tag in (
        "dashboard_hero_card",
        "dashboard_metric_strip",
        "dashboard_metric_table",
        "nav_workspace_label",
        "nav_status_card",
        "nav_status_title",
        "nav_status_value",
        "app_version",
    ):
        assert f'tag="{tag}"' not in MAIN


def test_retired_home_copy_is_not_constructed():
    for copy in (
        "DOTA 2 MOD ORCHESTRATION",
        "RELEASE ENGINE",
        "PATCH MATRIX  /  RELEASE CONSOLE",
        "Orchestrate your Dota build",
        "ANALYZE",
        "SNAPSHOT",
        "COMPOSE",
        "COMMAND DECK",
        "● PROTECTED",
    ):
        assert copy not in MAIN


def test_final_home_structure_exists_at_construction():
    for tag in (
        "dashboard_status_panel",
        "home_separator_before_actions",
        "dashboard_action_bar",
        "dashboard_action_buttons",
    ):
        assert f'tag="{tag}"' in MAIN
    assert 'with dpg.group(tag="header_brand_group", horizontal=False):' in MAIN
    assert 'dpg.add_text(f"RELEASE: {base.VERSION}", tag="app_product_name")' in MAIN
