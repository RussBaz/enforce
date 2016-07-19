import unittest

from enforce.types import is_type_of_type


class Animal:
        pass


class Pet(Animal):
    pass


class TestTypes(unittest.TestCase):
    
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

    def check_default_behaviour(self, type_a, type_b, local_variables=None, global_variables=None):
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
        self.check_default_behaviour(Pet, Animal)

    def test_covariant_from_str(self):
        self.check_covariant('Pet', 'Animal', local_variables=locals(), global_variables=globals())

    def test_contravariant_from_str(self):
        self.check_contravariant('Pet', 'Animal', local_variables=locals(), global_variables=globals())

    def test_invariant_from_strt(self):
        self.check_invariant('Pet', 'Animal', local_variables=locals(), global_variables=globals())

    def test_bivariant_from_str(self):
        self.check_bivariant('Pet', 'Animal', local_variables=locals(), global_variables=globals())

    def test_default_behaviour_from_str(self):
        self.check_default_behaviour('Pet', 'Animal', local_variables=locals(), global_variables=globals())


if __name__ == '__main__':
    unittest.main()
