import numbers
import typing
import unittest
from abc import ABC
from collections import namedtuple
from collections.abc import Sized

from enforce.types import (
    is_type_of_type,
    is_named_tuple,
    EnhancedTypeVar,
    Integer,
    Boolean,
)


class Animal(object):
    """
    Dummy class
    """

    pass


class Pet(Animal):
    """
    Dummy subclass of Animal
    """

    pass


class Chihuahua(Pet):
    """
    Dummy subclass of Pet
    """

    pass


class TestTypesChecking(unittest.TestCase):
    """
    Tests for the type checking function
    """

    def check_covariant(
        self, type_a, type_b, local_variables=None, global_variables=None
    ):
        """
        Template for performing certain covariant type checks
        """
        self.assertTrue(
            is_type_of_type(
                type_a,
                type_b,
                covariant=True,
                contravariant=False,
                local_variables=local_variables,
                global_variables=global_variables,
            )
        )
        self.assertFalse(
            is_type_of_type(
                type_b,
                type_a,
                covariant=True,
                contravariant=False,
                local_variables=local_variables,
                global_variables=global_variables,
            )
        )
        self.assertTrue(
            is_type_of_type(
                type_a,
                type_a,
                covariant=True,
                contravariant=False,
                local_variables=local_variables,
                global_variables=global_variables,
            )
        )

    def check_contravariant(
        self, type_a, type_b, local_variables=None, global_variables=None
    ):
        """
        Template for performing certain contravariant type checks
        """
        self.assertFalse(
            is_type_of_type(
                type_a,
                type_b,
                covariant=False,
                contravariant=True,
                local_variables=local_variables,
                global_variables=global_variables,
            )
        )
        self.assertTrue(
            is_type_of_type(
                type_b,
                type_a,
                covariant=False,
                contravariant=True,
                local_variables=local_variables,
                global_variables=global_variables,
            )
        )
        self.assertTrue(
            is_type_of_type(
                type_a,
                type_a,
                covariant=False,
                contravariant=True,
                local_variables=local_variables,
                global_variables=global_variables,
            )
        )

    def check_invariant(
        self, type_a, type_b, local_variables=None, global_variables=None
    ):
        """
        Template for performing certain invariant type checks
        """
        self.assertFalse(
            is_type_of_type(
                type_a,
                type_b,
                covariant=False,
                contravariant=False,
                local_variables=local_variables,
                global_variables=global_variables,
            )
        )
        self.assertFalse(
            is_type_of_type(
                type_b,
                type_a,
                covariant=False,
                contravariant=False,
                local_variables=local_variables,
                global_variables=global_variables,
            )
        )
        self.assertTrue(
            is_type_of_type(
                type_a,
                type_a,
                covariant=False,
                contravariant=False,
                local_variables=local_variables,
                global_variables=global_variables,
            )
        )

    def check_bivariant(
        self, type_a, type_b, local_variables=None, global_variables=None
    ):
        """
        Template for performing certain bivariant type checks
        """
        self.assertTrue(
            is_type_of_type(
                type_a,
                type_b,
                covariant=True,
                contravariant=True,
                local_variables=local_variables,
                global_variables=global_variables,
            )
        )
        self.assertTrue(
            is_type_of_type(
                type_b,
                type_a,
                covariant=True,
                contravariant=True,
                local_variables=local_variables,
                global_variables=global_variables,
            )
        )
        self.assertTrue(
            is_type_of_type(
                type_a,
                type_a,
                covariant=True,
                contravariant=True,
                local_variables=local_variables,
                global_variables=global_variables,
            )
        )

    def check_default_invariant_behaviour(
        self, type_a, type_b, local_variables=None, global_variables=None
    ):
        """
        Template for performing certain type checks which use default covariant/contravariant settings
        The default is invariant
        """
        self.assertFalse(
            is_type_of_type(
                type_a,
                type_b,
                local_variables=local_variables,
                global_variables=global_variables,
            )
        )
        self.assertFalse(
            is_type_of_type(
                type_b,
                type_a,
                local_variables=local_variables,
                global_variables=global_variables,
            )
        )
        self.assertTrue(
            is_type_of_type(
                type_a,
                type_a,
                local_variables=local_variables,
                global_variables=global_variables,
            )
        )

    def test_covariant(self):
        """
        Verifies that covariant type checking works as expected
        """
        self.check_covariant(Pet, Animal)

    def test_contravariant(self):
        """
        Verifies that contravariant type checking works as expected
        """
        self.check_contravariant(Pet, Animal)

    def test_invariant(self):
        """
        Verifies that invariant type checking works as expected
        """
        self.check_invariant(Pet, Animal)

    def test_bivariant(self):
        """
        Verifies that bivariant type checking works as expected
        """
        self.check_bivariant(Pet, Animal)

    def test_default_behaviour(self):
        """
        Verifies that the default beahviour is invariant and it works
        """
        self.check_default_invariant_behaviour(Pet, Animal)

    def test_none(self):
        """
        Verifies that type checking automatically replaces None with NoneType
        """
        self.assertTrue(is_type_of_type(None, None))
        self.assertTrue(is_type_of_type(type(None), None))
        self.assertTrue(is_type_of_type(None, None, covariant=True))
        self.assertTrue(is_type_of_type(None, None, contravariant=True))
        self.assertTrue(is_type_of_type(None, None, covariant=True, contravariant=True))

    def test_any(self):
        """
        Verifies that type checking works with Any construct
        """
        self.assertTrue(is_type_of_type(Animal, typing.Any))
        self.assertTrue(is_type_of_type(None, typing.Any))
        self.assertTrue(is_type_of_type(12, typing.Any))
        self.assertTrue(is_type_of_type([1, 3, "str"], typing.Any))
        self.assertEqual(type, typing.Any)

    def test_enhanced_type_var(self):
        """
        Verifies that type checking behaves exactly the same with an Enhanced TypeVar
        as it would with a default TypeVar
        """
        T = EnhancedTypeVar("T", str, int, Animal)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(int, T))
        self.assertTrue(is_type_of_type(str, T))
        self.assertFalse(is_type_of_type(Pet, T))
        self.assertFalse(is_type_of_type(None, T))

    def test_type_var_default(self):
        """
        Verifies that type checking works as expected with parameterless TypeVar
        and it works invariantly
        """
        T = typing.TypeVar("T")
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(None, T))

    def test_type_var_constrained(self):
        """
        Verifies that type checking respects the TypeVar constraints
        """
        T = typing.TypeVar("T", Animal, int)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

    def test_type_var_covariant(self):
        """
        Verifies that type checking works with covariant TypeVars
        """
        T = typing.TypeVar("T", Animal, int, covariant=True)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(Pet, T))
        self.assertTrue(is_type_of_type(Chihuahua, T))
        self.assertTrue(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

    def test_type_var_contravariant(self):
        """
        Verifies that type checking works with contravariant TypeVars
        """
        T = typing.TypeVar("T", Pet, int, contravariant=True)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(Pet, T))
        self.assertFalse(is_type_of_type(Chihuahua, T))
        self.assertTrue(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

    def test_enhanced_type_var_bivariant(self):
        """
        Default TypeVars cannot be bivariant
        This test verifies if an Enhanced version of it will properly checked
        """
        T = EnhancedTypeVar("T", Pet, int, covariant=True, contravariant=True)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(Pet, T))
        self.assertTrue(is_type_of_type(Chihuahua, T))
        self.assertTrue(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

    def test_type_var_bounded(self):
        """
        Verifies that type checking works with bounded TypeVars
        It uses Enhanced TypeVars for bivariant tests as default TypeVars cannot be bivariant
        """
        T = typing.TypeVar("T", bound=Animal)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertFalse(is_type_of_type(Pet, T))
        self.assertFalse(is_type_of_type(Chihuahua, T))
        self.assertFalse(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

        T = typing.TypeVar("T", covariant=True, bound=Animal)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(Pet, T))
        self.assertTrue(is_type_of_type(Chihuahua, T))
        self.assertFalse(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

        T = typing.TypeVar("T", contravariant=True, bound=Pet)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(Pet, T))
        self.assertFalse(is_type_of_type(Chihuahua, T))
        self.assertFalse(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

        # Bivariant TypeVars are not supported by default
        # Therefore, testing it with an Enhanced version of TypeVar
        T = EnhancedTypeVar("T", covariant=True, contravariant=True, bound=Pet)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(Pet, T))
        self.assertTrue(is_type_of_type(Chihuahua, T))
        self.assertFalse(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

    def test_any_from_str(self):
        """
        Verifies that type checking works with Any construct if it is provided as a string with the type name
        """
        self.assertTrue(is_type_of_type(Animal, "Any"))

    def test_none_from_str(self):
        """
        Verifies that type checking works with None if it is provided as a string with the type name
        """
        self.assertTrue(is_type_of_type(None, "None"))

    def test_covariant_from_str(self):
        """
        Verifies that covariant type checking works as expected when types are given as strings with type names
        """
        self.check_covariant(
            "Pet", "Animal", local_variables=locals(), global_variables=globals()
        )

    def test_contravariant_from_str(self):
        """
        Verifies that contravariant type checking works as expected when types are given as strings with type names
        """
        self.check_contravariant(
            "Pet", "Animal", local_variables=locals(), global_variables=globals()
        )

    def test_invariant_from_strt(self):
        """
        Verifies that invariant type checking works as expected when types are given as strings with type names
        """
        self.check_invariant(
            "Pet", "Animal", local_variables=locals(), global_variables=globals()
        )

    def test_bivariant_from_str(self):
        """
        Verifies that bivariant type checking works as expected when types are given as strings with type names
        """
        self.check_bivariant(
            "Pet", "Animal", local_variables=locals(), global_variables=globals()
        )

    def test_default_behaviour_from_str(self):
        """
        Verifies that the default type checking is invariant and
        that it works as expected when types are given as strings with type names
        """
        self.check_default_invariant_behaviour(
            "Pet", "Animal", local_variables=locals(), global_variables=globals()
        )

    def test_in_built_types(self):
        """
        Tests an unusual result found while testing tuples
        """
        a = (1, 1)  # Tuple
        b = 1  # Int
        c = 1.1  # Float
        d = 1 + 1j  # Complex
        e = None  # NoneType
        f = True  # Boolean
        g = {}  # Dictionary
        h = []  # List
        i = ""  # String
        k = b""  # Bytes

        self.assertTrue(is_type_of_type(type(a), typing.Tuple))
        self.assertTrue(is_type_of_type(type(b), Integer))
        self.assertTrue(is_type_of_type(type(c), numbers.Real))
        self.assertTrue(is_type_of_type(type(d), numbers.Complex))
        self.assertTrue(is_type_of_type(type(e), type(None)))
        self.assertTrue(is_type_of_type(type(f), Boolean))
        self.assertTrue(is_type_of_type(type(g), typing.Dict))
        self.assertTrue(is_type_of_type(type(h), typing.List))
        self.assertTrue(is_type_of_type(type(i), str))
        self.assertTrue(is_type_of_type(type(k), bytes))

    def test_complex_type_var(self):
        """
        Verifies that nested types, such as Unions, can be compared
        """
        T = typing.TypeVar("T", typing.Union[int, str], bytes)
        K = typing.TypeVar("K", typing.Optional[int], str)

        self.assertTrue(is_type_of_type(typing.Union[str, int], T))
        self.assertTrue(is_type_of_type(bytes, T))

        self.assertFalse(is_type_of_type(typing.Union[int, str, bytes], T))
        self.assertFalse(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(bytearray, T))

        self.assertTrue(is_type_of_type(typing.Optional[int], K))
        self.assertTrue(is_type_of_type(typing.Union[None, int], K))
        self.assertTrue(is_type_of_type(str, K))

        self.assertFalse(is_type_of_type(int, K))

    def test_generic_type(self):
        """
        Verifies that it can correctly compare generic types
        """
        from enforce.enforcers import GenericProxy

        T = typing.TypeVar("T")

        class A(typing.Generic[T]):
            pass

        class B(A):
            pass

        C = GenericProxy(A)

        self.assertFalse(is_type_of_type(A, typing.Generic))
        self.assertFalse(is_type_of_type(typing.Generic, A))
        self.assertTrue(is_type_of_type(A, typing.Generic, covariant=True))
        self.assertFalse(is_type_of_type(typing.Generic, A, covariant=True))
        self.assertFalse(is_type_of_type(A, typing.Generic, contravariant=True))
        self.assertTrue(is_type_of_type(typing.Generic, A, contravariant=True))
        self.assertTrue(
            is_type_of_type(A, typing.Generic, covariant=True, contravariant=True)
        )
        self.assertTrue(
            is_type_of_type(typing.Generic, A, covariant=True, contravariant=True)
        )

        self.assertFalse(is_type_of_type(B, typing.Generic))
        self.assertFalse(is_type_of_type(typing.Generic, B))
        self.assertTrue(is_type_of_type(B, typing.Generic, covariant=True))
        self.assertFalse(is_type_of_type(typing.Generic, B, covariant=True))
        self.assertFalse(is_type_of_type(B, typing.Generic, contravariant=True))
        self.assertTrue(is_type_of_type(typing.Generic, B, contravariant=True))
        self.assertTrue(
            is_type_of_type(B, typing.Generic, covariant=True, contravariant=True)
        )
        self.assertTrue(
            is_type_of_type(typing.Generic, B, covariant=True, contravariant=True)
        )

        self.assertFalse(is_type_of_type(C, typing.Generic))
        self.assertFalse(is_type_of_type(typing.Generic, C))
        self.assertTrue(is_type_of_type(C, typing.Generic, covariant=True))
        self.assertFalse(is_type_of_type(typing.Generic, C, covariant=True))
        self.assertFalse(is_type_of_type(C, typing.Generic, contravariant=True))
        self.assertTrue(is_type_of_type(typing.Generic, C, contravariant=True))
        self.assertTrue(
            is_type_of_type(C, typing.Generic, covariant=True, contravariant=True)
        )
        self.assertTrue(
            is_type_of_type(typing.Generic, C, covariant=True, contravariant=True)
        )

    def test_inbuilt_generics(self):
        """
        Verifies that type checking can correctly identify in-built generics
        """
        self.assertTrue(is_type_of_type(dict, typing.Mapping, covariant=True))

    def test_abc_registry(self):
        """
        Verifies that when a class is registered with ABC,
        unless a type check is invariant or subclasshook is defined on ABC,
        it would be a subclass of that ABC.
        This check must be done recursively.
        """

        # NOTE: Subclass test is a covariant check
        class A(ABC):
            pass

        class B(A):
            pass

        class C(ABC):
            pass

        class D(A):
            pass

        class E(object):
            pass

        class F(object):
            pass

        class G(object):
            pass

        A.register(C)
        A.register(D)
        A.register(G)
        A.register(tuple)
        C.register(F)

        self.assertTrue(is_type_of_type(A, A))

        self.assertFalse(is_type_of_type(B, A))
        self.assertFalse(is_type_of_type(A, B))

        self.assertFalse(is_type_of_type(C, A))
        self.assertFalse(is_type_of_type(A, C))

        self.assertFalse(is_type_of_type(D, A))
        self.assertFalse(is_type_of_type(A, D))

        self.assertFalse(is_type_of_type(E, A))
        self.assertFalse(is_type_of_type(A, E))

        self.assertFalse(is_type_of_type(F, A))
        self.assertFalse(is_type_of_type(A, F))

        self.assertFalse(is_type_of_type(G, A))
        self.assertFalse(is_type_of_type(A, G))

        self.assertFalse(is_type_of_type(tuple, A))
        self.assertFalse(is_type_of_type(A, tuple))

        self.assertTrue(is_type_of_type(A, A, covariant=True))
        self.assertTrue(is_type_of_type(A, A, contravariant=True))
        self.assertTrue(is_type_of_type(A, A, covariant=True, contravariant=True))

        self.assertTrue(is_type_of_type(B, A, covariant=True))
        self.assertFalse(is_type_of_type(A, B, covariant=True))
        self.assertFalse(is_type_of_type(B, A, contravariant=True))
        self.assertTrue(is_type_of_type(A, B, contravariant=True))
        self.assertTrue(is_type_of_type(B, A, covariant=True, contravariant=True))
        self.assertTrue(is_type_of_type(A, B, covariant=True, contravariant=True))

        self.assertTrue(is_type_of_type(C, A, covariant=True))
        self.assertFalse(is_type_of_type(A, C, covariant=True))
        self.assertFalse(is_type_of_type(C, A, contravariant=True))
        self.assertTrue(is_type_of_type(A, C, contravariant=True))
        self.assertTrue(is_type_of_type(C, A, covariant=True, contravariant=True))
        self.assertTrue(is_type_of_type(A, C, covariant=True, contravariant=True))

        self.assertTrue(is_type_of_type(D, A, covariant=True))
        self.assertFalse(is_type_of_type(A, D, covariant=True))
        self.assertFalse(is_type_of_type(D, A, contravariant=True))
        self.assertTrue(is_type_of_type(A, D, contravariant=True))
        self.assertTrue(is_type_of_type(D, A, covariant=True, contravariant=True))
        self.assertTrue(is_type_of_type(A, D, covariant=True, contravariant=True))

        self.assertFalse(is_type_of_type(E, A, covariant=True))
        self.assertFalse(is_type_of_type(A, E, covariant=True))
        self.assertFalse(is_type_of_type(E, A, contravariant=True))
        self.assertFalse(is_type_of_type(A, E, contravariant=True))
        self.assertFalse(is_type_of_type(E, A, covariant=True, contravariant=True))
        self.assertFalse(is_type_of_type(A, E, covariant=True, contravariant=True))

        self.assertTrue(is_type_of_type(F, A, covariant=True))
        self.assertFalse(is_type_of_type(A, F, covariant=True))
        self.assertFalse(is_type_of_type(F, A, contravariant=True))
        self.assertTrue(is_type_of_type(A, F, contravariant=True))
        self.assertTrue(is_type_of_type(F, A, covariant=True, contravariant=True))
        self.assertTrue(is_type_of_type(A, F, covariant=True, contravariant=True))

        self.assertTrue(is_type_of_type(G, A, covariant=True))
        self.assertFalse(is_type_of_type(A, G, covariant=True))
        self.assertFalse(is_type_of_type(G, A, contravariant=True))
        self.assertTrue(is_type_of_type(A, G, contravariant=True))
        self.assertTrue(is_type_of_type(G, A, covariant=True, contravariant=True))
        self.assertTrue(is_type_of_type(A, G, covariant=True, contravariant=True))

        self.assertTrue(is_type_of_type(tuple, A, covariant=True))
        self.assertFalse(is_type_of_type(A, tuple, covariant=True))
        self.assertFalse(is_type_of_type(tuple, A, contravariant=True))
        self.assertTrue(is_type_of_type(A, tuple, contravariant=True))
        self.assertTrue(is_type_of_type(tuple, A, covariant=True, contravariant=True))
        self.assertTrue(is_type_of_type(A, tuple, covariant=True, contravariant=True))

    def test_subclasshook(self):
        """
        Verifies that a subclasshook in ABC is respected and it takes precedence over ABC registry
        """

        class A(ABC):
            @classmethod
            def __subclasshook__(cls, C):
                try:
                    if cls is C.subclass_of:
                        return True
                    else:
                        return False
                except AttributeError:
                    return NotImplemented

        class B(A):
            pass

        class C(object):
            subclass_of = A

        class D(A):
            subclass_of = None

        class E(object):
            subclass_of = None

        A.register(E)

        self.assertTrue(is_type_of_type(A, A))

        self.assertFalse(is_type_of_type(B, A))
        self.assertFalse(is_type_of_type(A, B))
        self.assertFalse(is_type_of_type(C, A))
        self.assertFalse(is_type_of_type(A, C))
        self.assertFalse(is_type_of_type(D, A))
        self.assertFalse(is_type_of_type(A, D))
        self.assertFalse(is_type_of_type(E, A))
        self.assertFalse(is_type_of_type(A, E))

        self.assertTrue(is_type_of_type(A, A, covariant=True))
        self.assertTrue(is_type_of_type(A, A, contravariant=True))
        self.assertTrue(is_type_of_type(A, A, covariant=True, contravariant=True))

        self.assertTrue(is_type_of_type(B, A, covariant=True))
        self.assertFalse(is_type_of_type(A, B, covariant=True))
        self.assertFalse(is_type_of_type(B, A, contravariant=True))
        self.assertTrue(is_type_of_type(A, B, contravariant=True))
        self.assertTrue(is_type_of_type(B, A, covariant=True, contravariant=True))
        self.assertTrue(is_type_of_type(B, A, covariant=True, contravariant=True))

        self.assertTrue(is_type_of_type(C, A, covariant=True))
        self.assertFalse(is_type_of_type(A, C, covariant=True))
        self.assertFalse(is_type_of_type(C, A, contravariant=True))
        self.assertTrue(is_type_of_type(A, C, contravariant=True))
        self.assertTrue(is_type_of_type(C, A, covariant=True, contravariant=True))
        self.assertTrue(is_type_of_type(C, A, covariant=True, contravariant=True))

        self.assertFalse(is_type_of_type(D, A, covariant=True))
        self.assertFalse(is_type_of_type(A, D, covariant=True))
        self.assertFalse(is_type_of_type(D, A, contravariant=True))
        self.assertFalse(is_type_of_type(A, D, contravariant=True))
        self.assertFalse(is_type_of_type(D, A, covariant=True, contravariant=True))
        self.assertFalse(is_type_of_type(A, D, covariant=True, contravariant=True))

        self.assertFalse(is_type_of_type(E, A, covariant=True))
        self.assertFalse(is_type_of_type(A, E, covariant=True))
        self.assertFalse(is_type_of_type(E, A, contravariant=True))
        self.assertFalse(is_type_of_type(A, E, contravariant=True))
        self.assertFalse(is_type_of_type(E, A, covariant=True, contravariant=True))
        self.assertFalse(is_type_of_type(A, E, covariant=True, contravariant=True))

    def test_subclasscheck(self):
        """
        Verifies that subclasscheck is always respected if present
        """

        class A(object):
            @classmethod
            def __subclasscheck__(cls, C):
                try:
                    if cls is C.subclass_of:
                        return True
                    else:
                        return False
                except AttributeError:
                    return NotImplemented

        class B(A):
            pass

        class C(object):
            subclass_of = A

        class D(A):
            subclass_of = None

        class E(object):
            subclass_of = None

        self.assertTrue(is_type_of_type(A, A))

        self.assertFalse(is_type_of_type(B, A))
        self.assertFalse(is_type_of_type(A, B))
        self.assertFalse(is_type_of_type(C, A))
        self.assertFalse(is_type_of_type(A, C))
        self.assertFalse(is_type_of_type(D, A))
        self.assertFalse(is_type_of_type(A, D))
        self.assertFalse(is_type_of_type(E, A))
        self.assertFalse(is_type_of_type(A, E))

        self.assertTrue(is_type_of_type(A, A, covariant=True))
        self.assertTrue(is_type_of_type(A, A, contravariant=True))
        self.assertTrue(is_type_of_type(A, A, covariant=True, contravariant=True))

        self.assertTrue(is_type_of_type(B, A, covariant=True))
        self.assertFalse(is_type_of_type(A, B, covariant=True))
        self.assertFalse(is_type_of_type(B, A, contravariant=True))
        self.assertTrue(is_type_of_type(A, B, contravariant=True))
        self.assertTrue(is_type_of_type(B, A, covariant=True, contravariant=True))
        self.assertTrue(is_type_of_type(B, A, covariant=True, contravariant=True))

        self.assertTrue(is_type_of_type(C, A, covariant=True))
        self.assertFalse(is_type_of_type(A, C, covariant=True))
        self.assertFalse(is_type_of_type(C, A, contravariant=True))
        self.assertTrue(is_type_of_type(A, C, contravariant=True))
        self.assertTrue(is_type_of_type(C, A, covariant=True, contravariant=True))
        self.assertTrue(is_type_of_type(C, A, covariant=True, contravariant=True))

        self.assertFalse(is_type_of_type(D, A, covariant=True))
        self.assertFalse(is_type_of_type(A, D, covariant=True))
        self.assertFalse(is_type_of_type(D, A, contravariant=True))
        self.assertFalse(is_type_of_type(A, D, contravariant=True))
        self.assertFalse(is_type_of_type(D, A, covariant=True, contravariant=True))
        self.assertFalse(is_type_of_type(A, D, covariant=True, contravariant=True))

        self.assertFalse(is_type_of_type(E, A, covariant=True))
        self.assertFalse(is_type_of_type(A, E, covariant=True))
        self.assertFalse(is_type_of_type(E, A, contravariant=True))
        self.assertFalse(is_type_of_type(A, E, contravariant=True))
        self.assertFalse(is_type_of_type(E, A, covariant=True, contravariant=True))
        self.assertFalse(is_type_of_type(A, E, covariant=True, contravariant=True))

    def test_abc_protocols(self):
        """
        Verifies that ABC protocols are respected and working as expected
        """
        some_list = [1]
        list_type = type(some_list)
        self.assertTrue(is_type_of_type(list_type, Sized, covariant=True))

    def test_iterable(self):
        """
        Verifies if type/object is iterable
        """
        a = range(1, 12)
        ai = iter(a)

        at = type(a)
        ait = type(ai)

        def gen():
            yield 1

        gent = type(gen)

        g = gen()
        gt = type(g)

        self.assertTrue(is_type_of_type(at, typing.Iterable, covariant=True))
        self.assertTrue(is_type_of_type(ait, typing.Iterable, covariant=True))
        self.assertFalse(is_type_of_type(gent, typing.Iterable, covariant=True))
        self.assertTrue(is_type_of_type(gt, typing.Iterable, covariant=True))


class TestEnhancedTypeVar(unittest.TestCase):
    """
    Tests for the Enhanced TypeVar class
    """

    def test_init_enhanced_type_var(self):
        """
        Verifies that Enhanced TypeVar can be initialised like any other TypeVar
        or directly from an existing TypeVar
        """
        T = typing.TypeVar("T")
        ET = EnhancedTypeVar("T", type_var=T)
        self.assertTrue(T.__name__ == ET.__name__)
        self.assertTrue(T.__bound__ == ET.__bound__)
        self.assertTrue(T.__covariant__ == ET.__covariant__)
        self.assertTrue(T.__contravariant__ == ET.__contravariant__)
        self.assertTrue(T.__constraints__ == ET.__constraints__)
        self.assertEqual(repr(T), repr(ET))

        name = "ET"
        covariant = True
        contravariant = False
        bound = None
        constraints = (str, int)
        ET = EnhancedTypeVar(
            name,
            *constraints,
            covariant=covariant,
            contravariant=contravariant,
            bound=bound
        )
        self.assertEqual(ET.__name__, name)
        self.assertEqual(ET.__bound__, bound)
        self.assertEqual(ET.__covariant__, covariant)
        self.assertEqual(ET.__contravariant__, contravariant)
        self.assertEqual(ET.__constraints__, constraints)

    def test_bound_and_constrained(self):
        """
        Verifies that the Enhanced Type Variable can be both bound and constrained
        """
        ET = EnhancedTypeVar("T", int, str, bound=Boolean)

    def test_constraints(self):
        """
        Verifies that enhanced variable can return its constraints further constrained by the __bound__ value
        Also verifies that the result is always as a tuple
        """
        ETA = EnhancedTypeVar("ETA")
        ETB = EnhancedTypeVar("ETB", int, str)
        ETC = EnhancedTypeVar("ETC", bound=int)
        ETD = EnhancedTypeVar("ETD", int, str, bound=Boolean)

        self.assertTupleEqual(ETA.constraints, tuple())
        self.assertTupleEqual(ETB.constraints, (int, str))
        self.assertTupleEqual(ETC.constraints, (int,))
        self.assertTupleEqual(ETD.constraints, (Boolean,))

        self.assertIs(type(ETA.constraints), tuple)
        self.assertIs(type(ETB.constraints), tuple)
        self.assertIs(type(ETC.constraints), tuple)
        self.assertIs(type(ETD.constraints), tuple)

    def test_bivariant_type_var(self):
        """
        Verifies that it is possible to initialise a bivariant Enhanced TypeVar
        """
        ET = EnhancedTypeVar("ET", covariant=True, contravariant=True)
        self.assertTrue(ET.__covariant__)
        self.assertTrue(ET.__contravariant__)

    def test_representation(self):
        """
        Verifies that a consistent with TypeVar representation is shown when an Enhanced TypeVar is used
        The symbol for bivariant was randomly chosen as '*'
        """
        ET = EnhancedTypeVar("ET", covariant=True, contravariant=True)
        self.assertEqual(repr(ET), "*ET")
        ET = EnhancedTypeVar("ET", covariant=True)
        self.assertEqual(repr(ET), "+ET")
        ET = EnhancedTypeVar("ET", contravariant=True)
        self.assertEqual(repr(ET), "-ET")
        ET = EnhancedTypeVar("ET")
        self.assertEqual(repr(ET), "~ET")

    def test_equality(self):
        """
        Verifies that enhanced type variable can be compared to other enhanced variables
        """
        ETA = EnhancedTypeVar("ET", int, str, covariant=True, contravariant=True)
        ETB = EnhancedTypeVar("ET", int, str, covariant=True, contravariant=True)
        ETC = EnhancedTypeVar("ET", int, str, covariant=True, contravariant=False)
        ETD = typing.TypeVar("ET", int, str, covariant=True, contravariant=False)

        self.assertEqual(ETA, ETB)
        self.assertNotEqual(ETA, ETC)
        self.assertNotEqual(ETB, ETC)

        self.assertEqual(ETC, ETD)

    def test_single_constraint(self):
        """
        Verifies that a single constraint is not allowed and TypeError is raised
        """
        ET = EnhancedTypeVar("ET")
        ET = EnhancedTypeVar("ET", int, str)
        with self.assertRaises(TypeError):
            ET = EnhancedTypeVar("ET", int)


class TestTypeCheckingUtility(unittest.TestCase):
    def test_if_named_tuple(self):
        NT1 = namedtuple("NT1", "x, y, z")
        NT2 = typing.NamedTuple("NT2", [("x", int), ("y", int), ("z", int)])
        NT3 = tuple
        NT4 = int

        nt1 = NT1(1, 2, 3)
        nt2 = NT2(1, 2, 3)
        nt3 = NT3([1, 2, 3])
        nt4 = NT4(2)

        class NT5(tuple):
            pass

        nt5 = NT5([1, 2, 3])

        self.assertTrue(is_named_tuple(NT1))
        self.assertTrue(is_named_tuple(NT2))
        self.assertFalse(is_named_tuple(NT3))
        self.assertFalse(is_named_tuple(NT4))
        self.assertFalse(is_named_tuple(NT5))

        self.assertTrue(is_named_tuple(nt1))
        self.assertTrue(is_named_tuple(nt2))
        self.assertFalse(is_named_tuple(nt3))
        self.assertFalse(is_named_tuple(nt4))
        self.assertFalse(is_named_tuple(nt5))
