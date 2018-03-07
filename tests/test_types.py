import unittest
import numbers
import typing
from abc import ABC
from collections import namedtuple
from collections.abc import Sized

import pytest

from enforce.types import is_type_of_type, is_named_tuple, EnhancedTypeVar, Integer, Boolean


class Animal:
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


class TestTypesChecking:
    """
    Tests for the type checking function
    """

    def check_covariant(self, type_a, type_b, local_variables=None, global_variables=None):
        """
        Template for performing certain covariant type checks
        """
        assert is_type_of_type(type_a,
                               type_b,
                               covariant=True,
                               contravariant=False,
                               local_variables=local_variables,
                               global_variables=global_variables)
        assert not is_type_of_type(type_b,
                                   type_a,
                                   covariant=True,
                                   contravariant=False,
                                   local_variables=local_variables,
                                   global_variables=global_variables)
        assert is_type_of_type(type_a,
                               type_a,
                               covariant=True,
                               contravariant=False,
                               local_variables=local_variables,
                               global_variables=global_variables)

    def check_contravariant(self, type_a, type_b, local_variables=None, global_variables=None):
        """
        Template for performing certain contravariant type checks
        """
        assert not is_type_of_type(type_a,
                                   type_b,
                                   covariant=False,
                                   contravariant=True,
                                   local_variables=local_variables,
                                   global_variables=global_variables)
        assert is_type_of_type(type_b,
                               type_a,
                               covariant=False,
                               contravariant=True,
                               local_variables=local_variables,
                               global_variables=global_variables)
        assert is_type_of_type(type_a,
                               type_a,
                               covariant=False,
                               contravariant=True,
                               local_variables=local_variables,
                               global_variables=global_variables)

    def check_invariant(self, type_a, type_b, local_variables=None, global_variables=None):
        """
        Template for performing certain invariant type checks
        """
        assert not is_type_of_type(type_a,
                                   type_b,
                                   covariant=False,
                                   contravariant=False,
                                   local_variables=local_variables,
                                   global_variables=global_variables)
        assert not is_type_of_type(type_b,
                                   type_a,
                                   covariant=False,
                                   contravariant=False,
                                   local_variables=local_variables,
                                   global_variables=global_variables)
        assert is_type_of_type(type_a,
                               type_a,
                               covariant=False,
                               contravariant=False,
                               local_variables=local_variables,
                               global_variables=global_variables)

    def check_bivariant(self, type_a, type_b, local_variables=None, global_variables=None):
        """
        Template for performing certain bivariant type checks
        """
        assert is_type_of_type(type_a,
                               type_b,
                               covariant=True,
                               contravariant=True,
                               local_variables=local_variables,
                               global_variables=global_variables)
        assert is_type_of_type(type_b,
                               type_a,
                               covariant=True,
                               contravariant=True,
                               local_variables=local_variables,
                               global_variables=global_variables)
        assert is_type_of_type(type_a,
                               type_a,
                               covariant=True,
                               contravariant=True,
                               local_variables=local_variables,
                               global_variables=global_variables)

    def check_default_invariant_behaviour(self, type_a, type_b, local_variables=None, global_variables=None):
        """
        Template for performing certain type checks which use default covariant/contravariant settings
        The default is invariant
        """
        assert not is_type_of_type(type_a,
                                   type_b,
                                   local_variables=local_variables,
                                   global_variables=global_variables)
        assert not is_type_of_type(type_b,
                                   type_a,
                                   local_variables=local_variables,
                                   global_variables=global_variables)
        assert is_type_of_type(type_a,
                               type_a,
                               local_variables=local_variables,
                               global_variables=global_variables)

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
        assert is_type_of_type(None, None)
        assert is_type_of_type(type(None), None)
        assert is_type_of_type(None, None, covariant=True)
        assert is_type_of_type(None, None, contravariant=True)
        assert is_type_of_type(None, None, covariant=True, contravariant=True)

    def test_any(self):
        """
        Verifies that type checking works with Any construct
        """
        assert is_type_of_type(Animal, typing.Any)
        assert is_type_of_type(None, typing.Any)
        assert is_type_of_type(12, typing.Any)
        assert is_type_of_type([1, 3, 'str'], typing.Any)
        assert type, typing.Any

    def test_enhanced_type_var(self):
        """
        Verifies that type checking behaves exactly the same with an Enhanced TypeVar
        as it would with a default TypeVar
        """
        T = EnhancedTypeVar('T', str, int, Animal)
        assert is_type_of_type(Animal, T)
        assert is_type_of_type(int, T)
        assert is_type_of_type(str, T)
        assert not is_type_of_type(Pet, T)
        assert not is_type_of_type(None, T)

    def test_type_var_default(self):
        """
        Verifies that type checking works as expected with parameterless TypeVar
        and it works invariantly
        """
        T = typing.TypeVar('T')
        assert is_type_of_type(Animal, T)
        assert is_type_of_type(None, T)

    def test_type_var_constrained(self):
        """
        Verifies that type checking respects the TypeVar constraints
        """
        T = typing.TypeVar('T', Animal, int)
        assert is_type_of_type(Animal, T)
        assert is_type_of_type(int, T)
        assert not is_type_of_type(None, T)

    def test_type_var_covariant(self):
        """
        Verifies that type checking works with covariant TypeVars
        """
        T = typing.TypeVar('T', Animal, int, covariant=True)
        assert is_type_of_type(Animal, T)
        assert is_type_of_type(Pet, T)
        assert is_type_of_type(Chihuahua, T)
        assert is_type_of_type(int, T)
        assert not is_type_of_type(None, T)

    def test_type_var_contravariant(self):
        """
        Verifies that type checking works with contravariant TypeVars
        """
        T = typing.TypeVar('T', Pet, int, contravariant=True)
        assert is_type_of_type(Animal, T)
        assert is_type_of_type(Pet, T)
        assert not is_type_of_type(Chihuahua, T)
        assert is_type_of_type(int, T)
        assert not is_type_of_type(None, T)

    def test_enhanced_type_var_bivariant(self):
        """
        Default TypeVars cannot be bivariant
        This test verifies if an Enhanced version of it will properly checked
        """
        T = EnhancedTypeVar('T', Pet, int, covariant=True, contravariant=True)
        assert is_type_of_type(Animal, T)
        assert is_type_of_type(Pet, T)
        assert is_type_of_type(Chihuahua, T)
        assert is_type_of_type(int, T)
        assert not is_type_of_type(None, T)

    def test_type_var_bounded(self):
        """
        Verifies that type checking works with bounded TypeVars
        It uses Enhanced TypeVars for bivariant tests as default TypeVars cannot be bivariant
        """
        T = typing.TypeVar('T', bound=Animal)
        assert is_type_of_type(Animal, T)
        assert not is_type_of_type(Pet, T)
        assert not is_type_of_type(Chihuahua, T)
        assert not is_type_of_type(int, T)
        assert not is_type_of_type(None, T)

        T = typing.TypeVar('T', covariant=True, bound=Animal)
        assert is_type_of_type(Animal, T)
        assert is_type_of_type(Pet, T)
        assert is_type_of_type(Chihuahua, T)
        assert not is_type_of_type(int, T)
        assert not is_type_of_type(None, T)

        T = typing.TypeVar('T', contravariant=True, bound=Pet)
        assert is_type_of_type(Animal, T)
        assert is_type_of_type(Pet, T)
        assert not is_type_of_type(Chihuahua, T)
        assert not is_type_of_type(int, T)
        assert not is_type_of_type(None, T)

        # Bivariant TypeVars are not supported by default
        # Therefore, testing it with an Enhanced version of TypeVar
        T = EnhancedTypeVar('T', covariant=True, contravariant=True, bound=Pet)
        assert is_type_of_type(Animal, T)
        assert is_type_of_type(Pet, T)
        assert is_type_of_type(Chihuahua, T)
        assert not is_type_of_type(int, T)
        assert not is_type_of_type(None, T)

    def test_any_from_str(self):
        """
        Verifies that type checking works with Any construct if it is provided as a string with the type name
        """
        assert is_type_of_type(Animal, 'Any')

    def test_none_from_str(self):
        """
        Verifies that type checking works with None if it is provided as a string with the type name
        """
        assert is_type_of_type(None, 'None')

    def test_covariant_from_str(self):
        """
        Verifies that covariant type checking works as expected when types are given as strings with type names
        """
        self.check_covariant('Pet', 'Animal', local_variables=locals(), global_variables=globals())

    def test_contravariant_from_str(self):
        """
        Verifies that contravariant type checking works as expected when types are given as strings with type names
        """
        self.check_contravariant('Pet', 'Animal', local_variables=locals(), global_variables=globals())

    def test_invariant_from_strt(self):
        """
        Verifies that invariant type checking works as expected when types are given as strings with type names
        """
        self.check_invariant('Pet', 'Animal', local_variables=locals(), global_variables=globals())

    def test_bivariant_from_str(self):
        """
        Verifies that bivariant type checking works as expected when types are given as strings with type names
        """
        self.check_bivariant('Pet', 'Animal', local_variables=locals(), global_variables=globals())

    def test_default_behaviour_from_str(self):
        """
        Verifies that the default type checking is invariant and
        that it works as expected when types are given as strings with type names
        """
        self.check_default_invariant_behaviour('Pet', 'Animal', local_variables=locals(), global_variables=globals())

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
        i = ''  # String
        k = b''  # Bytes

        assert is_type_of_type(type(a), typing.Tuple)
        assert is_type_of_type(type(b), Integer)
        assert is_type_of_type(type(c), numbers.Real)
        assert is_type_of_type(type(d), numbers.Complex)
        assert is_type_of_type(type(e), type(None))
        assert is_type_of_type(type(f), Boolean)
        assert is_type_of_type(type(g), typing.Dict)
        assert is_type_of_type(type(h), typing.List)
        assert is_type_of_type(type(i), str)
        assert is_type_of_type(type(k), bytes)

    def test_complex_type_var(self):
        """
        Verifies that nested types, such as Unions, can be compared
        """
        T = typing.TypeVar('T', typing.Union[int, str], bytes)
        K = typing.TypeVar('K', typing.Optional[int], str)

        assert is_type_of_type(typing.Union[str, int], T)
        assert is_type_of_type(bytes, T)

        assert not is_type_of_type(typing.Union[int, str, bytes], T)
        assert not is_type_of_type(int, T)
        assert not is_type_of_type(bytearray, T)

        assert is_type_of_type(typing.Optional[int], K)
        assert is_type_of_type(typing.Union[None, int], K)
        assert is_type_of_type(str, K)

        assert not is_type_of_type(int, K)

    def test_generic_type(self):
        """
        Verifies that it can correctly compare generic types
        """
        from enforce.enforcers import GenericProxy

        T = typing.TypeVar('T')

        class A(typing.Generic[T]):
            pass

        class B(A):
            pass

        C = GenericProxy(A)

        assert not is_type_of_type(A, typing.Generic)
        assert not is_type_of_type(typing.Generic, A)
        assert is_type_of_type(A, typing.Generic, covariant=True)
        assert not is_type_of_type(typing.Generic, A, covariant=True)
        assert not is_type_of_type(A, typing.Generic, contravariant=True)
        assert is_type_of_type(typing.Generic, A, contravariant=True)
        assert is_type_of_type(A, typing.Generic, covariant=True, contravariant=True)
        assert is_type_of_type(typing.Generic, A, covariant=True, contravariant=True)

        assert not is_type_of_type(B, typing.Generic)
        assert not is_type_of_type(typing.Generic, B)
        assert is_type_of_type(B, typing.Generic, covariant=True)
        assert not is_type_of_type(typing.Generic, B, covariant=True)
        assert not is_type_of_type(B, typing.Generic, contravariant=True)
        assert is_type_of_type(typing.Generic, B, contravariant=True)
        assert is_type_of_type(B, typing.Generic, covariant=True, contravariant=True)
        assert is_type_of_type(typing.Generic, B, covariant=True, contravariant=True)

        assert not is_type_of_type(C, typing.Generic)
        assert not is_type_of_type(typing.Generic, C)
        assert is_type_of_type(C, typing.Generic, covariant=True)
        assert not is_type_of_type(typing.Generic, C, covariant=True)
        assert not is_type_of_type(C, typing.Generic, contravariant=True)
        assert is_type_of_type(typing.Generic, C, contravariant=True)
        assert is_type_of_type(C, typing.Generic, covariant=True, contravariant=True)
        assert is_type_of_type(typing.Generic, C, covariant=True, contravariant=True)

    def test_inbuilt_generics(self):
        """
        Verifies that type checking can correctly identify in-built generics
        """
        assert is_type_of_type(dict, typing.Mapping, covariant=True)

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

        class E:
            pass

        class F:
            pass

        class G:
            pass

        A.register(C)
        A.register(D)
        A.register(G)
        A.register(tuple)
        C.register(F)

        assert is_type_of_type(A, A)

        assert not is_type_of_type(B, A)
        assert not is_type_of_type(A, B)

        assert not is_type_of_type(C, A)
        assert not is_type_of_type(A, C)

        assert not is_type_of_type(D, A)
        assert not is_type_of_type(A, D)

        assert not is_type_of_type(E, A)
        assert not is_type_of_type(A, E)

        assert not is_type_of_type(F, A)
        assert not is_type_of_type(A, F)

        assert not is_type_of_type(G, A)
        assert not is_type_of_type(A, G)

        assert not is_type_of_type(tuple, A)
        assert not is_type_of_type(A, tuple)

        assert is_type_of_type(A, A, covariant=True)
        assert is_type_of_type(A, A, contravariant=True)
        assert is_type_of_type(A, A, covariant=True, contravariant=True)

        assert is_type_of_type(B, A, covariant=True)
        assert not is_type_of_type(A, B, covariant=True)
        assert not is_type_of_type(B, A, contravariant=True)
        assert is_type_of_type(A, B, contravariant=True)
        assert is_type_of_type(B, A, covariant=True, contravariant=True)
        assert is_type_of_type(A, B, covariant=True, contravariant=True)

        assert is_type_of_type(C, A, covariant=True)
        assert not is_type_of_type(A, C, covariant=True)
        assert not is_type_of_type(C, A, contravariant=True)
        assert is_type_of_type(A, C, contravariant=True)
        assert is_type_of_type(C, A, covariant=True, contravariant=True)
        assert is_type_of_type(A, C, covariant=True, contravariant=True)

        assert is_type_of_type(D, A, covariant=True)
        assert not is_type_of_type(A, D, covariant=True)
        assert not is_type_of_type(D, A, contravariant=True)
        assert is_type_of_type(A, D, contravariant=True)
        assert is_type_of_type(D, A, covariant=True, contravariant=True)
        assert is_type_of_type(A, D, covariant=True, contravariant=True)

        assert not is_type_of_type(E, A, covariant=True)
        assert not is_type_of_type(A, E, covariant=True)
        assert not is_type_of_type(E, A, contravariant=True)
        assert not is_type_of_type(A, E, contravariant=True)
        assert not is_type_of_type(E, A, covariant=True, contravariant=True)
        assert not is_type_of_type(A, E, covariant=True, contravariant=True)

        assert is_type_of_type(F, A, covariant=True)
        assert not is_type_of_type(A, F, covariant=True)
        assert not is_type_of_type(F, A, contravariant=True)
        assert is_type_of_type(A, F, contravariant=True)
        assert is_type_of_type(F, A, covariant=True, contravariant=True)
        assert is_type_of_type(A, F, covariant=True, contravariant=True)

        assert is_type_of_type(G, A, covariant=True)
        assert not is_type_of_type(A, G, covariant=True)
        assert not is_type_of_type(G, A, contravariant=True)
        assert is_type_of_type(A, G, contravariant=True)
        assert is_type_of_type(G, A, covariant=True, contravariant=True)
        assert is_type_of_type(A, G, covariant=True, contravariant=True)

        assert is_type_of_type(tuple, A, covariant=True)
        assert not is_type_of_type(A, tuple, covariant=True)
        assert not is_type_of_type(tuple, A, contravariant=True)
        assert is_type_of_type(A, tuple, contravariant=True)
        assert is_type_of_type(tuple, A, covariant=True, contravariant=True)
        assert is_type_of_type(A, tuple, covariant=True, contravariant=True)

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

        class C:
            subclass_of = A

        class D(A):
            subclass_of = None

        class E:
            subclass_of = None

        A.register(E)

        assert is_type_of_type(A, A)

        assert not is_type_of_type(B, A)
        assert not is_type_of_type(A, B)
        assert not is_type_of_type(C, A)
        assert not is_type_of_type(A, C)
        assert not is_type_of_type(D, A)
        assert not is_type_of_type(A, D)
        assert not is_type_of_type(E, A)
        assert not is_type_of_type(A, E)

        assert is_type_of_type(A, A, covariant=True)
        assert is_type_of_type(A, A, contravariant=True)
        assert is_type_of_type(A, A, covariant=True, contravariant=True)

        assert is_type_of_type(B, A, covariant=True)
        assert not is_type_of_type(A, B, covariant=True)
        assert not is_type_of_type(B, A, contravariant=True)
        assert is_type_of_type(A, B, contravariant=True)
        assert is_type_of_type(B, A, covariant=True, contravariant=True)
        assert is_type_of_type(B, A, covariant=True, contravariant=True)

        assert is_type_of_type(C, A, covariant=True)
        assert not is_type_of_type(A, C, covariant=True)
        assert not is_type_of_type(C, A, contravariant=True)
        assert is_type_of_type(A, C, contravariant=True)
        assert is_type_of_type(C, A, covariant=True, contravariant=True)
        assert is_type_of_type(C, A, covariant=True, contravariant=True)

        assert not is_type_of_type(D, A, covariant=True)
        assert not is_type_of_type(A, D, covariant=True)
        assert not is_type_of_type(D, A, contravariant=True)
        assert not is_type_of_type(A, D, contravariant=True)
        assert not is_type_of_type(D, A, covariant=True, contravariant=True)
        assert not is_type_of_type(A, D, covariant=True, contravariant=True)

        assert not is_type_of_type(E, A, covariant=True)
        assert not is_type_of_type(A, E, covariant=True)
        assert not is_type_of_type(E, A, contravariant=True)
        assert not is_type_of_type(A, E, contravariant=True)
        assert not is_type_of_type(E, A, covariant=True, contravariant=True)
        assert not is_type_of_type(A, E, covariant=True, contravariant=True)

    def test_subclasscheck(self):
        """
        Verifies that subclasscheck is always respected if present
        """

        class A:
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

        class C:
            subclass_of = A

        class D(A):
            subclass_of = None

        class E:
            subclass_of = None

        assert is_type_of_type(A, A)

        assert not is_type_of_type(B, A)
        assert not is_type_of_type(A, B)
        assert not is_type_of_type(C, A)
        assert not is_type_of_type(A, C)
        assert not is_type_of_type(D, A)
        assert not is_type_of_type(A, D)
        assert not is_type_of_type(E, A)
        assert not is_type_of_type(A, E)

        assert is_type_of_type(A, A, covariant=True)
        assert is_type_of_type(A, A, contravariant=True)
        assert is_type_of_type(A, A, covariant=True, contravariant=True)

        assert is_type_of_type(B, A, covariant=True)
        assert not is_type_of_type(A, B, covariant=True)
        assert not is_type_of_type(B, A, contravariant=True)
        assert is_type_of_type(A, B, contravariant=True)
        assert is_type_of_type(B, A, covariant=True, contravariant=True)
        assert is_type_of_type(B, A, covariant=True, contravariant=True)

        assert is_type_of_type(C, A, covariant=True)
        assert not is_type_of_type(A, C, covariant=True)
        assert not is_type_of_type(C, A, contravariant=True)
        assert is_type_of_type(A, C, contravariant=True)
        assert is_type_of_type(C, A, covariant=True, contravariant=True)
        assert is_type_of_type(C, A, covariant=True, contravariant=True)

        assert not is_type_of_type(D, A, covariant=True)
        assert not is_type_of_type(A, D, covariant=True)
        assert not is_type_of_type(D, A, contravariant=True)
        assert not is_type_of_type(A, D, contravariant=True)
        assert not is_type_of_type(D, A, covariant=True, contravariant=True)
        assert not is_type_of_type(A, D, covariant=True, contravariant=True)

        assert not is_type_of_type(E, A, covariant=True)
        assert not is_type_of_type(A, E, covariant=True)
        assert not is_type_of_type(E, A, contravariant=True)
        assert not is_type_of_type(A, E, contravariant=True)
        assert not is_type_of_type(E, A, covariant=True, contravariant=True)
        assert not is_type_of_type(A, E, covariant=True, contravariant=True)

    def test_abc_protocols(self):
        """
        Verifies that ABC protocols are respected and working as expected
        """
        some_list = [1]
        list_type = type(some_list)
        assert is_type_of_type(list_type, Sized, covariant=True)

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

        assert is_type_of_type(at, typing.Iterable, covariant=True)
        assert is_type_of_type(ait, typing.Iterable, covariant=True)
        assert not is_type_of_type(gent, typing.Iterable, covariant=True)
        assert is_type_of_type(gt, typing.Iterable, covariant=True)


class TestEnhancedTypeVar:
    """
    Tests for the Enhanced TypeVar class
    """

    def test_init_enhanced_type_var(self):
        """
        Verifies that Enhanced TypeVar can be initialised like any other TypeVar
        or directly from an existing TypeVar
        """
        T = typing.TypeVar('T')
        ET = EnhancedTypeVar('T', type_var=T)
        assert T.__name__ == ET.__name__
        assert T.__bound__ == ET.__bound__
        assert T.__covariant__ == ET.__covariant__
        assert T.__contravariant__ == ET.__contravariant__
        assert T.__constraints__ == ET.__constraints__
        assert repr(T) == repr(ET)

        name = 'ET'
        covariant = True
        contravariant = False
        bound = None
        constraints = (str, int)
        ET = EnhancedTypeVar(name, *constraints, covariant=covariant, contravariant=contravariant, bound=bound)
        assert ET.__name__ == name
        assert ET.__bound__ == bound
        assert ET.__covariant__ == covariant
        assert ET.__contravariant__ == contravariant
        assert ET.__constraints__ == constraints

    def test_bound_and_constrained(self):
        """
        Verifies that the Enhanced Type Variable can be both bound and constrained
        """
        ET = EnhancedTypeVar('T', int, str, bound=Boolean)

    def test_constraints(self):
        """
        Verifies that enhanced variable can return its constraints further constrained by the __bound__ value
        Also verifies that the result is always as a tuple
        """
        ETA = EnhancedTypeVar('ETA')
        ETB = EnhancedTypeVar('ETB', int, str)
        ETC = EnhancedTypeVar('ETC', bound=int)
        ETD = EnhancedTypeVar('ETD', int, str, bound=Boolean)

        assert ETA.constraints == tuple()
        assert ETB.constraints == (int, str)
        assert ETC.constraints == (int,)
        assert ETD.constraints == (Boolean,)

        assert type(ETA.constraints) is tuple
        assert type(ETB.constraints) is tuple
        assert type(ETC.constraints) is tuple
        assert type(ETD.constraints) is tuple

    def test_bivariant_type_var(self):
        """
        Verifies that it is possible to initialise a bivariant Enhanced TypeVar
        """
        ET = EnhancedTypeVar('ET', covariant=True, contravariant=True)
        assert ET.__covariant__
        assert ET.__contravariant__

    def test_representation(self):
        """
        Verifies that a consistent with TypeVar representation is shown when an Enhanced TypeVar is used
        The symbol for bivariant was randomly chosen as '*'
        """
        ET = EnhancedTypeVar('ET', covariant=True, contravariant=True)
        assert repr(ET) == '*ET'
        ET = EnhancedTypeVar('ET', covariant=True)
        assert repr(ET) == '+ET'
        ET = EnhancedTypeVar('ET', contravariant=True)
        assert repr(ET) == '-ET'
        ET = EnhancedTypeVar('ET')
        assert repr(ET) == '~ET'

    def test_equality(self):
        """
        Verifies that enhanced type variable can be compared to other enhanced variables
        """
        ETA = EnhancedTypeVar('ET', int, str, covariant=True, contravariant=True)
        ETB = EnhancedTypeVar('ET', int, str, covariant=True, contravariant=True)
        ETC = EnhancedTypeVar('ET', int, str, covariant=True, contravariant=False)
        ETD = typing.TypeVar('ET', int, str, covariant=True, contravariant=False)

        assert ETA == ETB
        assert ETA != ETC
        assert ETB != ETC

        assert ETC == ETD

    def test_single_constraint(self):
        """
        Verifies that a single constraint is not allowed and TypeError is raised
        """
        ET = EnhancedTypeVar('ET')
        ET = EnhancedTypeVar('ET', int, str)
        with pytest.raises(TypeError):
            ET = EnhancedTypeVar('ET', int)


class TestTypeCheckingUtility:

    def test_if_named_tuple(self):
        NT1 = namedtuple('NT1', 'x, y, z')
        NT2 = typing.NamedTuple('NT2', [('x', int), ('y', int), ('z', int)])
        NT3 = tuple
        NT4 = int

        nt1 = NT1(1, 2, 3)
        nt2 = NT2(1, 2, 3)
        nt3 = NT3([1, 2, 3])
        nt4 = NT4(2)

        class NT5(tuple):
            pass

        nt5 = NT5([1, 2, 3])

        assert is_named_tuple(NT1)
        assert is_named_tuple(NT2)
        assert not is_named_tuple(NT3)
        assert not is_named_tuple(NT4)
        assert not is_named_tuple(NT5)

        assert is_named_tuple(nt1)
        assert is_named_tuple(nt2)
        assert not is_named_tuple(nt3)
        assert not is_named_tuple(nt4)
        assert not is_named_tuple(nt5)
