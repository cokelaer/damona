from damona.admin import stats


def test_stats():
    stats()


def test_get_software_names():
    from damona.admin import get_software_names

    names = get_software_names()
    assert len(names) > 0
    # names must not include the version
    assert all(":" not in x for x in names)
