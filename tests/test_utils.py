import unittest

from enforce.utils import run_lazy_function, merge_dictionaries


class UtilsTests(unittest.TestCase):
    def test_visit(self):
        """
        Verifies that 'visit' function returns a result returned by the given generator
        """

        def generator_foo(a):
            result = yield generator_multiply_add(a, a + 1)
            result = yield generator_multiply_add(result, result + 1)
            yield result

        def generator_multiply_add(a, b):
            yield a + 2 * b

        result = run_lazy_function(generator_foo(1))

        self.assertEqual(result, 17)

    def test_dictionary_merge(self):
        """
        Verifies that merge dictionaries returns new dictionary with combined results of given two
        The second (update) dictionary is given a priority
        It also has an optional parameter, to merge lists instead of replacing them if both keys exist
        """
        d1 = {}
        d2 = {"a": "a", "b": "b"}
        d3 = {"a": "a", "l": [1, 2]}
        d4 = {"l": [3], "c": "c"}
        d5 = {"l": "l"}

        e1 = {"a": "a", "b": "b"}
        e2 = {"a": "a", "b": "b", "l": [1, 2]}
        e3 = {"a": "a", "l": [3], "c": "c"}
        e4 = {"a": "a", "l": [1, 2, 3], "c": "c"}
        e5 = {"l": "l", "c": "c"}
        e6 = {"l": [3], "c": "c"}

        r1 = merge_dictionaries(d1, d2)
        r2 = merge_dictionaries(d2, d3)
        r3 = merge_dictionaries(d3, d4)
        r4 = merge_dictionaries(d3, d4, merge_lists=True)
        r5 = merge_dictionaries(d4, d5)
        r6 = merge_dictionaries(d5, d4)

        self.assertDictEqual(r1, e1)
        self.assertDictEqual(r2, e2)
        self.assertDictEqual(r3, e3)
        self.assertDictEqual(r4, e4)
        self.assertDictEqual(r5, e5)
        self.assertDictEqual(r6, e6)

        self.assertDictEqual(d1, {})


if __name__ == "__main__":
    unittest.main()
