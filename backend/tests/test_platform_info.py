from app.services.platform_info import get_platform_info, get_all_platforms


def test_gmc_info():
    info = get_platform_info("gmc")
    assert info is not None
    assert info["platform"] == "gmc"
    assert len(info["required_fields"]) > 0
    assert all("field" in f and "description" in f for f in info["required_fields"])


def test_ceneo_info():
    info = get_platform_info("ceneo")
    assert info is not None
    assert info["platform"] == "ceneo"
    assert len(info["tips"]) > 0


def test_all_platforms_have_info():
    for platform in ["ceneo", "gmc", "facebook", "allegro", "skapiec", "domodi"]:
        info = get_platform_info(platform)
        assert info is not None, f"Missing info for {platform}"
        assert "required_fields" in info
        assert "recommended_fields" in info
        assert "tips" in info


def test_unknown_platform():
    info = get_platform_info("nonexistent")
    assert info is None


def test_get_all_platforms():
    platforms = get_all_platforms()
    assert len(platforms) == 6
    assert all("platform" in p and "name" in p and "required_count" in p for p in platforms)
