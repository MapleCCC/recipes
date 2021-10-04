from recipes.classlib import singleton_class


def test_singleton_class() -> None:
    @singleton_class
    class A:
        pass

    assert A() is A()
