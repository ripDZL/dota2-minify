from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
D2PFX = ROOT / "V2_STAGING" / "Minify" / "plugins" / "d2pfx" / "src"


def test_v2_d2pfx_restores_compact_960px_layout():
    browser = (D2PFX / "D2pfxBrowser.svelte").read_text(encoding="utf-8")
    sidebar = (D2PFX / "lib" / "components" / "Sidebar.svelte").read_text(encoding="utf-8")
    card = (D2PFX / "lib" / "components" / "ModCard.svelte").read_text(encoding="utf-8")
    header = (D2PFX / "lib" / "components" / "Header.svelte").read_text(encoding="utf-8")

    assert "grid-template-columns: repeat(4, minmax(0, 1fr));" in browser
    assert "@media (max-width: 1280px)" in browser
    assert "grid-template-columns: repeat(3, minmax(0, 1fr));" in browser
    assert "@media (max-width: 1080px)" in browser
    assert "grid-template-columns: repeat(2, minmax(0, 1fr));" in browser
    assert "@media (max-width: 960px)" in browser
    assert "grid-template-columns: minmax(0, 1fr);" in browser
    assert 'class="action-message" role="status" aria-live="polite"' in browser
    assert "@media (max-width: 960px)" in sidebar
    assert "width: 148px;" in sidebar

    assert "@media (max-width: 960px)" in card
    assert "grid-template-columns: 112px minmax(0, 1fr) 120px;" in card
    assert "height: 66px;" in card
    assert "mod.updated_label" in card
    assert "mod.preview_fallback_url" in card
    assert "previewSrc = mod.preview_fallback_url" in card

    assert "@media (max-width: 960px)" in header
    assert ".cat-info p" in header
    assert "display: none;" in header
