import unittest
import numbers
from typing import TypeVar, Any, Tuple, Dict, List

from enforce.types import is_type_of_type, EnahncedTypeVar, Integer, Boolean


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


class TestTypesChecking(unittest.TestCase):
    """
    Tests for the type checking function
    """
    
    def check_covariant(self, type_a, type_b, local_variables=None, global_variables=None):
        """
        Template for performing certain covariant type checks
        """
        self.assertTrue(is_type_of_type(type_a,
                                        type_b,
                                        covariant=True,
                                        contravariant=False,
                                        local_variables=local_variables,
                                        global_variables=global_variables))
        self.assertFalse(is_type_of_type(type_b,
                                         type_a,
                                         covariant=True,
                                         contravariant=False,
                                        local_variables=local_variables,
                                        global_variables=global_variables))
        self.assertTrue(is_type_of_type(type_a,
                                        type_a,
                                        covariant=True,
                                        contravariant=False,
                                        local_variables=local_variables,
                                        global_variables=global_variables))

    def check_contravariant(self, type_a, type_b, local_variables=None, global_variables=None):
        """
        Template for performing certain contravariant type checks
        """
        self.assertFalse(is_type_of_type(type_a,
                                        type_b,
                                        covariant=False,
                                        contravariant=True,
                                        local_variables=local_variables,
                                        global_variables=global_variables))
        self.assertTrue(is_type_of_type(type_b,
                                         type_a,
                                         covariant=False,
                                         contravariant=True,
                                        local_variables=local_variables,
                                        global_variables=global_variables))
        self.assertTrue(is_type_of_type(type_a,
                                        type_a,
                                        covariant=False,
                                        contravariant=True,
                                        local_variables=local_variables,
                                        global_variables=global_variables))

    def check_invariant(self, type_a, type_b, local_variables=None, global_variables=None):
        """
        Template for performing certain invariant type checks
        """
        self.assertFalse(is_type_of_type(type_a,
                                        type_b,
                                        covariant=False,
                                        contravariant=False,
                                        local_variables=local_variables,
                                        global_variables=global_variables))
        self.assertFalse(is_type_of_type(type_b,
                                         type_a,
                                         covariant=False,
                                         contravariant=False,
                                        local_variables=local_variables,
                                        global_variables=global_variables))
        self.assertTrue(is_type_of_type(type_a,
                                        type_a,
                                        covariant=False,
                                        contravariant=False,
                                        local_variables=local_variables,
                                        global_variables=global_variables))

    def check_bivariant(self, type_a, type_b, local_variables=None, global_variables=None):
        """
        Template for performing certain bivariant type checks
        """
        self.assertTrue(is_type_of_type(type_a,
                                        type_b,
                                        covariant=True,
                                        contravariant=True,
                                        local_variables=local_variables,
                                        global_variables=global_variables))
        self.assertTrue(is_type_of_type(type_b,
                                         type_a,
                                         covariant=True,
                                         contravariant=True,
                                        local_variables=local_variables,
                                        global_variables=global_variables))
        self.assertTrue(is_type_of_type(type_a,
                                        type_a,
                                        covariant=True,
                                        contravariant=True,
                                        local_variables=local_variables,
                                        global_variables=global_variables))

    def check_default_invariant_behaviour(self, type_a, type_b, local_variables=None, global_variables=None):
        """
        Template for performing certain type checks which use default covariant/contravariant settings
        The default is invariant
        """
        self.assertFalse(is_type_of_type(type_a,
                                        type_b,
                                        local_variables=local_variables,
                                        global_variables=global_variables))
        self.assertFalse(is_type_of_type(type_b,
                                         type_a,
                                        local_variables=local_variables,
                                        global_variables=global_variables))
        self.assertTrue(is_type_of_type(type_a,
                                        type_a,
                                        local_variables=local_variables,
                                        global_variables=global_variables))

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

    def test_any(self):
        """
        Verifies that type checking works with Any construct
        """
        self.assertTrue(is_type_of_type(Animal, Any))
        self.assertTrue(is_type_of_type(None, Any))

    def test_enhanced_type_var(self):
        """
        Verifies that type checking behaves exactly the same with an Enhanced TypeVar
        as it would with a default TypeVar
        """
        T = EnahncedTypeVar('T', str, int, Animal)
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
        T = TypeVar('T')
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(None, T))

    def test_type_var_constrained(self):
        """
        Verifies that type checking respects the TypeVar constraints
        """
        T = TypeVar('T', Animal, int)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

    def test_type_var_covariant(self):
        """
        Verifies that type checking works with covariant TypeVars
        """
        T = TypeVar('T', Animal, int, covariant=True)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(Pet, T))
        self.assertTrue(is_type_of_type(Chihuahua, T))
        self.assertTrue(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

    def test_type_var_contravariant(self):
        """
        Verifies that type checking works with contravariant TypeVars
        """
        T = TypeVar('T', Pet, int, contravariant=True)
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
        T = EnahncedTypeVar('T', Pet, int, covariant=True, contravariant=True)
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
        T = TypeVar('T', bound=Animal)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertFalse(is_type_of_type(Pet, T))
        self.assertFalse(is_type_of_type(Chihuahua, T))
        self.assertFalse(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

        T = TypeVar('T', covariant=True, bound=Animal)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(Pet, T))
        self.assertTrue(is_type_of_type(Chihuahua, T))
        self.assertFalse(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

        T = TypeVar('T', contravariant=True, bound=Pet)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(Pet, T))
        self.assertFalse(is_type_of_type(Chihuahua, T))
        self.assertFalse(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))
        
        # Bivariant TypeVars are not supported by default
        # Therefore, testing it with an Enhanced version of TypeVar
        T = EnahncedTypeVar('T', covariant=True, contravariant=True, bound=Pet)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(Pet, T))
        self.assertTrue(is_type_of_type(Chihuahua, T))
        self.assertFalse(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

    def test_any_from_str(self):
        """
        Verifies that type checking works with Any construct if it is provided as a string with the type name
        """
        self.assertTrue(is_type_of_type(Animal, 'Any'))

    def test_none_from_str(self):
        """
        Verifies that type checking works with None if it is provided as a string with the type name
        """
        self.assertTrue(is_type_of_type(None, 'None'))

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

        self.assertTrue(is_type_of_type(type(a), Tuple))
        self.assertTrue(is_type_of_type(type(b), Integer))
        self.assertTrue(is_type_of_type(type(c), numbers.Real))
        self.assertTrue(is_type_of_type(type(d), numbers.Complex))
        self.assertTrue(is_type_of_type(type(e), type(None)))
        self.assertTrue(is_type_of_type(type(f), Boolean))
        self.assertTrue(is_type_of_type(type(g), Dict))
        self.assertTrue(is_type_of_type(type(h), List))
        self.assertTrue(is_type_of_type(type(i), str))


class TestTypesEnhanced(unittest.TestCase):
    """
    Tests for the Enhanced TypeVar class
    """
    
    def test_init_enhanced_type_var(self):
        """
        Verifies that Enhanced TypeVar can be initialised like any other TypeVar
        or directly from an existing TypeVar
        """
        T = TypeVar('T')
        ET = EnahncedTypeVar('T', type_var=T)
        self.assertEqual(T.__name__, ET.__name__)
        self.assertEqual(T.__bound__, ET.__bound__)
        self.assertEqual(T.__covariant__, ET.__covariant__)
        self.assertEqual(T.__contravariant__, ET.__contravariant__)
        self.assertEqual(T.__constraints__, ET.__constraints__)
        self.assertIs(T, ET.type_var)
        self.assertEqual(repr(T), repr(ET))

        name = 'ET'
        covariant = True
        contravariant = False
        bound = None
        constraints = (str, int)
        ET = EnahncedTypeVar(name, *constraints, covariant=covariant, contravariant=contravariant, bound=bound)
        self.assertEqual(ET.__name__, name)
        self.assertEqual(ET.__bound__, bound)
        self.assertEqual(ET.__covariant__, covariant)
        self.assertEqual(ET.__contravariant__, contravariant)
        self.assertEqual(ET.__constraints__, constraints)
        self.assertIsNotNone(ET.type_var)

    def test_bivariant_type_var(self):
        """
        Verifies that it is possible to initialise a bivariant Enhanced TypeVar
        """
        ET = EnahncedTypeVar('ET', covariant=True, contravariant=True)
        self.assertTrue(ET.__covariant__)
        self.assertTrue(ET.__contravariant__)

    def test_representation(self):
        """
        Verifies that a consistent with TypeVar representation is shown when an Enhanced TypeVar is used
        The symbol for bivariant was randomly chosen as '*'
        """
        ET = EnahncedTypeVar('ET', covariant=True, contravariant=True)
        self.assertEqual(repr(ET), '*ET')
        ET = EnahncedTypeVar('ET', covariant=True)
        self.assertEqual(repr(ET), '+ET')
        ET = EnahncedTypeVar('ET', contravariant=True)
        self.assertEqual(repr(ET), '-ET')
        ET = EnahncedTypeVar('ET')
        self.assertEqual(repr(ET), '~ET')


if __name__ == '__main__':
    unittest.main()
