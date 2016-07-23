import unittest
from typing import TypeVar, Any

from enforce.types import is_type_of_type


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
        self.check_covariant(Pet, Animal)

    def test_contravariant(self):
        self.check_contravariant(Pet, Animal)

    def test_invariant(self):
        self.check_invariant(Pet, Animal)

    def test_bivariant(self):
        self.check_bivariant(Pet, Animal)

    def test_default_behaviour(self):
        self.check_default_invariant_behaviour(Pet, Animal)

    def test_none(self):
        self.assertTrue(is_type_of_type(None, None))

    def test_any(self):
        self.assertTrue(is_type_of_type(Animal, Any))
        self.assertTrue(is_type_of_type(None, Any))

    def test_type_var_default(self):
        T = TypeVar('T')
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(None, T))

    def test_type_var_constrained(self):
        T = TypeVar('T', Animal, int)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

    def test_type_var_covariant(self):
        T = TypeVar('T', Animal, int, covariant=True)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(Pet, T))
        self.assertTrue(is_type_of_type(Chihuahua, T))
        self.assertTrue(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

    def test_type_var_contravariant(self):
        T = TypeVar('T', Pet, int, contravariant=True)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(Pet, T))
        self.assertFalse(is_type_of_type(Chihuahua, T))
        self.assertTrue(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

    @unittest.skip('Standard TypeVars cannot be bivariant')
    def test_type_var_bivariant(self):
        T = TypeVar('T', Pet, int, covariant=True, contravariant=True)
        self.assertTrue(is_type_of_type(Animal, T))
        self.assertTrue(is_type_of_type(Pet, T))
        self.assertTrue(is_type_of_type(Chihuahua, T))
        self.assertTrue(is_type_of_type(int, T))
        self.assertFalse(is_type_of_type(None, T))

    def test_type_var_bounded(self):
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
        #T = TypeVar('T', covariant=True, contravariant=True, bound=Pet)
        #self.assertTrue(is_type_of_type(Animal, T))
        #self.assertTrue(is_type_of_type(Pet, T))
        #self.assertTrue(is_type_of_type(Chihuahua, T))
        #self.assertFalse(is_type_of_type(int, T))
        #self.assertFalse(is_type_of_type(None, T))

    def test_any_from_str(self):
        self.assertTrue(is_type_of_type(Animal, 'Any'))

    def test_none_from_str(self):
        self.assertTrue(is_type_of_type(None, 'None'))

    def test_covariant_from_str(self):
        self.check_covariant('Pet', 'Animal', local_variables=locals(), global_variables=globals())

    def test_contravariant_from_str(self):
        self.check_contravariant('Pet', 'Animal', local_variables=locals(), global_variables=globals())

    def test_invariant_from_strt(self):
        self.check_invariant('Pet', 'Animal', local_variables=locals(), global_variables=globals())

    def test_bivariant_from_str(self):
        self.check_bivariant('Pet', 'Animal', local_variables=locals(), global_variables=globals())

    def test_default_behaviour_from_str(self):
        self.check_default_invariant_behaviour('Pet', 'Animal', local_variables=locals(), global_variables=globals())


class TestTypesEnhanced(unittest.TestCase):
    """
    Tests for the Enhanced TypeVar class
    """
    pass


if __name__ == '__main__':
    unittest.main()
