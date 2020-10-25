import unittest

from enforce import runtime_validation


class ConcurrentRunTests(unittest.TestCase):
    def test_threading(self):
        import concurrent.futures

        ASSERT_ENABLED = True

        def test_runner(widget_number):
            widgets = [x for x in range(widget_number)]
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                for score in executor.map(test_one_widget, widgets):
                    if ASSERT_ENABLED:
                        assert isinstance(score, int)

        @runtime_validation
        def test_one_widget(widget_id: int) -> int:
            # print('ID:', widget_id)
            score = widget_inspector(widget_id, a="foo", b=4, c="bar")
            return score

        @runtime_validation
        def widget_inspector(widget_id: int, a: str, b: int, c: str) -> int:
            if ASSERT_ENABLED:
                assert isinstance(widget_id, int)
                assert isinstance(a, str)
                assert isinstance(b, int)
                assert isinstance(c, str)
            return b

        for i in range(100):
            test_runner(100)
            print(".", end="", flush=True)
        print("test success")

    @unittest.skip("I do not even know how to debug this issue!")
    def test_processing(self):
        import concurrent.futures

        ASSERT_ENABLED = True

        def test_runner(widget_number):
            widgets = [x for x in range(widget_number)]
            with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
                for score in executor.map(test_one_widget, widgets):
                    if ASSERT_ENABLED:
                        assert isinstance(score, int)

        @runtime_validation
        def test_one_widget(widget_id: int) -> int:
            # print('ID:', widget_id)
            score = widget_inspector(widget_id, a="foo", b=4, c="bar")
            return score

        @runtime_validation
        def widget_inspector(widget_id: int, a: str, b: int, c: str) -> int:
            if ASSERT_ENABLED:
                assert isinstance(widget_id, int)
                assert isinstance(a, str)
                assert isinstance(b, int)
                assert isinstance(c, str)
            return b

        for i in range(100):
            test_runner(100)
            print(".", end="", flush=True)
        print("test success")
