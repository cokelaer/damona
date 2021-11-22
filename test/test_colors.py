from damona.colors import Colors


def test_colors():
    c = Colors()
    c.failed("test")
    c.bold("test")
    c.purple("test")
    c.underlined("test")
    c.fail("test")
    c.error("test")
    c.warning("test")
    c.green("test")
    c.blue("test")
