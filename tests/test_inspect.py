from recipes.inspect import get_function_body_source


class TestGetFunctionBodySource:
    def test_normal_case(self) -> None:
        def f():
            a = 1
            b = 2

        assert get_function_body_source(f) == "\n    a = 1\n    b = 2\n"

    def test_lambda(self) -> None:
        assert get_function_body_source(lambda: 321) == "321"

    def test_method(self) -> None:
        class A:
            def b(self):
                a = 1
                b = 2

        assert get_function_body_source(A.b) == "\n    a = 1\n    b = 2\n"
        assert get_function_body_source(A().b) == "\n    a = 1\n    b = 2\n"
