from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REMOVE_WEATHER_BLACKLISTS = (
    REPO_ROOT / "Minify/mods/Remove Weather Effects/blacklist.txt",
    REPO_ROOT / "V2_STAGING/Minify/mods/Remove Weather Effects/blacklist.txt",
)


def _active_lines(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def test_remove_weather_does_not_blank_skybox_materials():
    for blacklist in REMOVE_WEATHER_BLACKLISTS:
        lines = _active_lines(blacklist)
        assert not any(line.startswith("materials/skybox/") for line in lines), blacklist


def test_remove_weather_still_suppresses_rain_particles_and_thunder():
    expected_sounds = {
        f"sounds/ambient/soundscapes/rain_thunder0{index}.vsnd_c"
        for index in range(1, 6)
    }

    for blacklist in REMOVE_WEATHER_BLACKLISTS:
        lines = set(_active_lines(blacklist))
        assert ">>particles/rain_fx" in lines
        assert expected_sounds.issubset(lines)
