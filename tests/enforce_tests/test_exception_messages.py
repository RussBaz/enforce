import re
import typing
import unittest

from enforce import config, runtime_validation
from enforce.exceptions import RuntimeTypeError


class ExceptionMessageTests(unittest.TestCase):
    """
    Tests for validating a correct exception messages are returned
    """
    def setUp(self):
        self.prefix_message = "\n  The following runtime type errors were encountered:"
        self.input_error_message = "Argument '{0}' was not of type {1}. Actual type was {2}."
        self.return_error_message = "Return value was not of type {0}. Actual type was {1}."
        self.errors = {
            'errors': [],
            'hints': {}
        }

        def error_processor(p, ex, e, h, r):
            self.errors['errors'] = e
            self.errors['hints'] = h
            raise ex('Please ignore me')

        config(reset=True)
        config({'errors': {'processor': error_processor}})

    def tearDown(self):
        config(reset=True)

    def generate_strict_function(self, inputs: typing.List[typing.Tuple[str, str]], returns: typing.Optional[str], result) -> typing.Callable:
        template = """
@runtime_validation
def func({inputs}) {returns}:
    return data
"""
        inputs = tuple(': '.join(input_pair) for input_pair in inputs)
        inputs = ', '.join(inputs)
        returns = '' if returns is None else '-> ' + returns
        formatted_template = template.format(inputs=inputs, returns=returns)

        scope_data = {
            'data': result,
            'typing': typing,
            'runtime_validation': runtime_validation
        }

        exec(formatted_template, scope_data)

        func = scope_data['func']

        return self.skip_type_errors(func)

    def skip_type_errors(self, func):
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RuntimeTypeError:
                pass

        return wrapped

    def get_error(self, pos=None):
        if pos is None:
            return self.errors['errors']
        else:
            return self.errors['errors'][pos]

    def assert_first_error_is(self, parameter_name: str, expected_value: str):
        self.assertEqual(self.first_error, (parameter_name, expected_value))

    @property
    def first_error(self):
        return self.get_error(0)

    @property
    def hints(self):
        return self.errors['hints']

    def generateExceptionPattern(self, messages, is_return=False):
        if is_return:
            expected_message = self.return_error_message.format(*messages)
            expected_message = '.*' + re.escape(expected_message) + '.*'
        else:
            expected_message = self.input_error_message.format(*messages)
            expected_message = '.*' + re.escape(expected_message) + '.*'

        pattern = re.compile(expected_message)

        return pattern

    def test_simple_exceptions(self):
        sample_function = self.generate_strict_function(
            inputs=[('a', 'int')],
            returns='str',
            result=12
        )

        sample_function('12')
        self.assertEqual(self.first_error, ('a', 'str'))

        sample_function(12)

        self.assertEqual(self.first_error, ('return', 'int'))

    def test_list_exceptions(self):
        sample_function = self.generate_strict_function(
            inputs=[('a', 'typing.List[int]')],
            returns='str',
            result=12
        )

        sample_function(12)
        self.assert_first_error_is('a', 'int')

        sample_function('12')
        self.assert_first_error_is('a', 'str')

        sample_function(['12'])
        self.assert_first_error_is('a', 'typing.List[str]')

        sample_function([12])
        self.assert_first_error_is('return', 'int')

    def test_set_exceptions(self):
        sample_function = self.generate_strict_function(
            inputs=[('a', 'typing.Set[int]')],
            returns='str',
            result=12)

        sample_function(12)
        self.assert_first_error_is('a', 'int')

        sample_function({'12'})
        self.assert_first_error_is('a', 'typing.Set[str]')

        sample_function({12})
        self.assert_first_error_is('return', 'int')

    def test_dict_exceptions(self):
        scope = {
            'data': None,
            'type_alias': typing.Dict[str, int]
        }

        @self.skip_type_errors
        @runtime_validation
        def sample_function(a: scope['type_alias']) -> scope['type_alias']:
            return scope['data']

        sample_function(12)
        self.assert_first_error_is('a', 'int')

        # If outer container is different, there is no need to check inner contents
        sample_function({'12'})
        self.assert_first_error_is('a', 'typing.Set')

        sample_function({'s': 12.0})
        self.assert_first_error_is('a', 'typing.Dict[str, float]')

        scope['data'] = 12

        sample_function({'s': 12})
        self.assert_first_error_is('return', 'int')

        scope['data'] = {'12'}

        sample_function({'s': 12})
        self.assert_first_error_is('return', 'typing.Set')

        scope['data'] = {'s': 12.0}

        sample_function({'s': 12})
        self.assert_first_error_is('return', 'typing.Dict[str, float]')

        scope = {
            'data': None,
            'type_alias': typing.Dict[str, typing.Dict[str, typing.Optional[int]]]
        }

        @self.skip_type_errors
        @runtime_validation
        def sample_function(a: scope['type_alias']) -> scope['type_alias']:
            return scope['data']

        sample_function({'hello': {'world': 12, 'w': None, 'r': 12.0}})

        self.assert_first_error_is('a', 'typing.Dict[str, typing.Dict[str, typing.Union[NoneType, float, int]]]')

    def test_union_exceptions(self):
        sample_function = self.generate_strict_function(
            inputs=[('a', 'typing.Union[int, str]')],
            returns='typing.List[typing.Union[int, str]]',
            result=[None]
        )

        sample_function(None)
        self.assert_first_error_is('a', 'NoneType')

        sample_function([None])
        self.assert_first_error_is('a', 'typing.List')

        sample_function(12)
        self.assert_first_error_is('return', 'typing.List[NoneType]')

    def test_tuple_exception(self):
        sample_function = self.generate_strict_function(
            inputs=[('a', 'typing.Tuple[int, typing.Union[int, str]]')],
            returns='int',
            result=12
        )

        sample_function(('1', 2))
        self.assert_first_error_is('a', 'typing.Tuple[str, int]')

        sample_function = self.generate_strict_function(
            inputs=[('a', 'typing.Tuple[int, int, int]')],
            returns='None',
            result=None
        )

        sample_function((1, 2))
        self.assert_first_error_is('a', 'typing.Tuple[int, int]')

        sample_function((1, 2, 'abc'))
        self.assert_first_error_is('a', 'typing.Tuple[int, int, str]')

    def test_named_tuple_exception(self):
        from collections import namedtuple

        MyNamedTuple = typing.NamedTuple('MyNamedTuple', [('a', int), ('b', str)])

        @self.skip_type_errors
        @runtime_validation
        def foo(data: MyNamedTuple):
            return str(data.b) + str(data.a)

        foo(MyNamedTuple(10, 10))

        error_string = str(MyNamedTuple) + " with incorrect arguments: a -> <class 'int'>, b -> <class 'int'>"
        self.assert_first_error_is('data', error_string)

        foo((10, 'ten'))
        self.assert_first_error_is('data', 'typing.Tuple')

        foo(12)
        self.assert_first_error_is('data', 'int')

        foo(namedtuple('MyNamedTuple', ['a', 'b'])(10, 'ten'))
        self.assert_first_error_is('data', 'untyped MyNamedTuple')

        foo(None)
        self.assert_first_error_is('data', 'NoneType')

    def test_named_tuple_incorrect_number_arguments(self):
        N = typing.NamedTuple('N', [('a', int), ('b', str)])
        N = runtime_validation(N)

        expected_error = "N() got an unexpected keyword argument: 'c'"
        with self.assertRaises(TypeError) as e:
            n = N(1, c=2)

        self.assertEqual(str(e.exception), expected_error)

        expected_error = "N() missing 2 keyword arguments: 'a', 'b'"
        with self.assertRaises(TypeError) as e:
            n = N()

        self.assertEqual(str(e.exception), expected_error)

        expected_error = "N() missing 1 keyword arguments: 'b'"
        with self.assertRaises(TypeError) as e:
            n = N(1)

        self.assertEqual(str(e.exception), expected_error)

        expected_error = "N() takes 2 positional arguments but 3 were given"
        with self.assertRaises(TypeError) as e:
            n = N(1, 2, 3)

        self.assertEqual(str(e.exception), expected_error)

        expected_error = "N() takes 2 positional arguments but 4 were given"
        with self.assertRaises(TypeError) as e:
            n = N(1, 2, 3, b=3)

        self.assertEqual(str(e.exception), expected_error)

    def test_callable_exception(self):
        sample_function = self.generate_strict_function(
            inputs=[('a', 'typing.Callable[[typing.Any], None]')],
            returns='int',
            result=12
        )

        @runtime_validation
        def foo(a: typing.Dict) -> None:
            pass

        sample_function(foo)
        self.assert_first_error_is('a', 'typing.Callable[[typing.Dict], NoneType]')

    def test_forgotten_self_exception(self):
        def hello():
            print("Hello, World!")

        class A:
            pass

        A.hello = hello

        A = runtime_validation(A)

        a = A()

        expected_exception_message = 'hello() was given an incorrect number of positional arguments'

        with self.assertRaises(TypeError) as e:
            a.hello()

        self.assertEqual(str(e.exception), expected_exception_message)