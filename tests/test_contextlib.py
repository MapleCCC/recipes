from recipes.contextlib import skip_context, literal_block


def test_skip_context() -> None:

    a = 0
    with skip_context():
        a = 1
    assert a == 0


def test_literal_block() -> None:

    with literal_block() as source:
        a = 1
        b = 2

    assert source == "a = 1\nb = 2"
