import unittest

from enforce.settings import Settings, _GLOBAL_SETTINGS, ModeChoices, config


class SettingsTests(unittest.TestCase):

    def setUp(self):
        config(reset=True)

    def tearDown(self):
        config(reset=True)

    def test_can_create_settings_instance(self):
        """
        Verifies that Settings instance and especially its enabled property work as intended
        """
        settings = Settings()

        self.assertFalse(settings.enabled)
        self.assertFalse(settings)
        self.assertEqual(settings.group, 'default')

        settings.enabled = False

        self.assertFalse(settings.enabled)
        self.assertFalse(settings)
        self.assertTrue(_GLOBAL_SETTINGS['enabled'])

        settings.enabled = True

        self.assertTrue(settings.enabled)
        self.assertTrue(settings)
        self.assertTrue(_GLOBAL_SETTINGS['enabled'])

        #############################################

        settings = Settings(enabled=True)

        self.assertTrue(settings.enabled)
        self.assertTrue(settings)
        self.assertEqual(settings.group, 'default')

        settings.enabled = False

        self.assertFalse(settings.enabled)
        self.assertFalse(settings)
        self.assertTrue(_GLOBAL_SETTINGS['enabled'])

        settings.enabled = True

        self.assertTrue(settings.enabled)
        self.assertTrue(settings)
        self.assertTrue(_GLOBAL_SETTINGS['enabled'])

        #############################################

        settings = Settings(enabled=False)

        self.assertFalse(settings.enabled)
        self.assertFalse(settings)
        self.assertEqual(settings.group, 'default')

        settings.enabled = True

        self.assertTrue(settings.enabled)
        self.assertTrue(settings)
        self.assertTrue(_GLOBAL_SETTINGS['enabled'])

        settings.enabled = False

        self.assertFalse(settings.enabled)
        self.assertFalse(settings)
        self.assertTrue(_GLOBAL_SETTINGS['enabled'])

    def test_groups(self):
        """
        Verifies that settings can be  assigned to a group different from the default
        Also, verifies that local enabled takes precedence over the group enabled status
        """
        settings = Settings(group='my_group')

        self.assertFalse(settings)
        self.assertEqual(settings.group, 'my_group')

        config({'groups': {'set': {'my_group': True}}})

        self.assertTrue(settings)

        settings.enabled = False

        self.assertFalse(settings)
        self.assertTrue(_GLOBAL_SETTINGS['enabled'])

        settings.enabled = True

        self.assertTrue(settings)
        self.assertTrue(_GLOBAL_SETTINGS['enabled'])

        ##################
        config(reset=True)

        settings = Settings(group='my_group', enabled=True)

        self.assertTrue(settings)
        self.assertEqual(settings.group, 'my_group')

        config({'groups': {'set': {'my_group': True}}})

        self.assertTrue(settings)

        settings.enabled = False

        self.assertFalse(settings)
        self.assertTrue(_GLOBAL_SETTINGS['enabled'])

        settings.enabled = True

        self.assertTrue(settings)
        self.assertTrue(_GLOBAL_SETTINGS['enabled'])

        ##################
        config(reset=True)

        settings = Settings(group='my_group', enabled=False)

        self.assertFalse(settings)
        self.assertEqual(settings.group, 'my_group')

        config({'groups': {'set': {'my_group': True}}})

        self.assertFalse(settings)

        settings.enabled = True

        self.assertTrue(settings)
        self.assertTrue(_GLOBAL_SETTINGS['enabled'])

        settings.enabled = False

        self.assertFalse(settings)
        self.assertTrue(_GLOBAL_SETTINGS['enabled'])

    def test_config_global_enabled(self):
        """
        Verifies that global enabled option can be set as expected
        """
        self.assertTrue(_GLOBAL_SETTINGS['enabled'])
        config({'enabled': False})
        self.assertFalse(_GLOBAL_SETTINGS['enabled'])
        config({'enabled': None})
        self.assertFalse(_GLOBAL_SETTINGS['enabled'])
        config({'enabled': True})
        self.assertTrue(_GLOBAL_SETTINGS['enabled'])
        config({'enabled': None})
        self.assertTrue(_GLOBAL_SETTINGS['enabled'])

    def test_config_groups_default(self):
        """
        Verifies that changing the status of a default group works as expected
        The default group status cannot be changed as any other group
        The special option 'default' must be used
        """
        self.assertTrue(_GLOBAL_SETTINGS['default'])
        config({'groups': {'default': False}})
        self.assertFalse(_GLOBAL_SETTINGS['default'])
        config({'groups': {'default': None}})
        self.assertFalse(_GLOBAL_SETTINGS['default'])
        config({'groups': {'default': True}})
        self.assertTrue(_GLOBAL_SETTINGS['default'])
        config({'groups': {'default': None}})
        self.assertTrue(_GLOBAL_SETTINGS['default'])

        with self.assertRaises(KeyError):
            config({'groups': {'set': {'default': None}}})

    def test_config_groups_previous_options(self):
        """
        Verifies that xyz_previous options work as expected
        Available options:
        # 1. Clear - deletes all previously available groups
        # 2. Enable - sets all previously available groups to True
        # 3. Disable - sets all previously available groups to False
        """
        self.assertEqual(_GLOBAL_SETTINGS['groups'], {})

        self.assertTrue(_GLOBAL_SETTINGS['default'])
        _GLOBAL_SETTINGS['groups']['group1'] = True
        _GLOBAL_SETTINGS['groups']['group2'] = False
        _GLOBAL_SETTINGS['groups']['group3'] = True

        config({'groups': {'disable_previous': True}})
        self.assertTrue(all(not v for v in _GLOBAL_SETTINGS['groups'].values()))
        self.assertTrue(_GLOBAL_SETTINGS['default'])

        _GLOBAL_SETTINGS['groups']['group1'] = True
        _GLOBAL_SETTINGS['groups']['group2'] = False
        _GLOBAL_SETTINGS['groups']['group3'] = True

        config({'groups': {'disable_previous': False}})
        self.assertTrue(_GLOBAL_SETTINGS['default'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group1'])
        self.assertFalse(_GLOBAL_SETTINGS['groups']['group2'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group3'])

        _GLOBAL_SETTINGS['groups']['group1'] = True
        _GLOBAL_SETTINGS['groups']['group2'] = False
        _GLOBAL_SETTINGS['groups']['group3'] = True

        config({'groups': {'disable_previous': None}})
        self.assertTrue(_GLOBAL_SETTINGS['default'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group1'])
        self.assertFalse(_GLOBAL_SETTINGS['groups']['group2'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group3'])

        #############################################

        _GLOBAL_SETTINGS['groups']['group1'] = True
        _GLOBAL_SETTINGS['groups']['group2'] = False
        _GLOBAL_SETTINGS['groups']['group3'] = True

        config({'groups': {'enable_previous': True}})
        self.assertTrue(all(bool(v) for v in _GLOBAL_SETTINGS['groups'].values()))
        self.assertTrue(_GLOBAL_SETTINGS['default'])

        _GLOBAL_SETTINGS['groups']['group1'] = True
        _GLOBAL_SETTINGS['groups']['group2'] = False
        _GLOBAL_SETTINGS['groups']['group3'] = True

        config({'groups': {'enable_previous': False}})
        self.assertTrue(_GLOBAL_SETTINGS['default'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group1'])
        self.assertFalse(_GLOBAL_SETTINGS['groups']['group2'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group3'])

        _GLOBAL_SETTINGS['groups']['group1'] = True
        _GLOBAL_SETTINGS['groups']['group2'] = False
        _GLOBAL_SETTINGS['groups']['group3'] = True

        config({'groups': {'enable_previous': None}})
        self.assertTrue(_GLOBAL_SETTINGS['default'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group1'])
        self.assertFalse(_GLOBAL_SETTINGS['groups']['group2'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group3'])

        #############################################

        _GLOBAL_SETTINGS['groups']['group1'] = True
        _GLOBAL_SETTINGS['groups']['group2'] = False
        _GLOBAL_SETTINGS['groups']['group3'] = True

        config({'groups': {'clear_previous': True}})
        self.assertEqual(_GLOBAL_SETTINGS['groups'], {})
        self.assertTrue(_GLOBAL_SETTINGS['default'])

        _GLOBAL_SETTINGS['groups']['group1'] = True
        _GLOBAL_SETTINGS['groups']['group2'] = False
        _GLOBAL_SETTINGS['groups']['group3'] = True

        config({'groups': {'clear_previous': False}})
        self.assertTrue(_GLOBAL_SETTINGS['default'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group1'])
        self.assertFalse(_GLOBAL_SETTINGS['groups']['group2'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group3'])

        _GLOBAL_SETTINGS['groups']['group1'] = True
        _GLOBAL_SETTINGS['groups']['group2'] = False
        _GLOBAL_SETTINGS['groups']['group3'] = True

        config({'groups': {'clear_previous': None}})
        self.assertTrue(_GLOBAL_SETTINGS['default'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group1'])
        self.assertFalse(_GLOBAL_SETTINGS['groups']['group2'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group3'])

    def test_config_groups_set(self):
        """
        Verifies that setting groups status works as expected
        """
        self.assertEqual(_GLOBAL_SETTINGS['groups'], {})

        _GLOBAL_SETTINGS['groups']['group4'] = True
        self.assertDictEqual(_GLOBAL_SETTINGS['groups'], {'group4': True})

        config({'groups': {'set': {'group1': True, 'group2': False, 'group3': None}}})

        self.assertEqual(len(_GLOBAL_SETTINGS['groups']), 3)
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group1'])
        self.assertFalse(_GLOBAL_SETTINGS['groups']['group2'])
        self.assertFalse(_GLOBAL_SETTINGS['groups'].get('group3', False))
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group4'])

        config({'groups': {'set': {'group1': False, 'group2': None, 'group3': True}}})

        self.assertEqual(len(_GLOBAL_SETTINGS['groups']), 4)
        self.assertFalse(_GLOBAL_SETTINGS['groups']['group1'])
        self.assertFalse(_GLOBAL_SETTINGS['groups']['group2'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group3'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group4'])

        config({'groups': {'set': {'group4': False}}})

        self.assertEqual(len(_GLOBAL_SETTINGS['groups']), 4)
        self.assertFalse(_GLOBAL_SETTINGS['groups']['group1'])
        self.assertFalse(_GLOBAL_SETTINGS['groups']['group2'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group3'])
        self.assertFalse(_GLOBAL_SETTINGS['groups']['group4'])

        with self.assertRaises(KeyError):
            config({'groups': {'hello_world': 1}})

    def test_config_groups_altogether(self):
        """
        Verifies that all groups config options can work with each other
        """
        config_update = {
            'groups': {
                    'set': {
                        'group1': True,
                        'group2': False,
                        'group3': None
                        },
                    'default': False,
                    'disable_previous': True,
                    'enable_previous': True
                },
            }

        _GLOBAL_SETTINGS['groups']['group4'] = False

        config(config_update)

        self.assertEqual(len(_GLOBAL_SETTINGS['groups']), 3)
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group1'])
        self.assertFalse(_GLOBAL_SETTINGS['groups']['group2'])
        self.assertNotIn('group3', _GLOBAL_SETTINGS['groups'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group4'])
        self.assertFalse(_GLOBAL_SETTINGS['default'])

        config_update = {
            'groups': {
                    'set': {
                        'group1': False
                        },
                    'default': True,
                    'disable_previous': True,
                    'enable_previous': True,
                    'clear_previous': True
                },
            }

        config(config_update)

        self.assertEqual(len(_GLOBAL_SETTINGS['groups']), 1)
        self.assertFalse(_GLOBAL_SETTINGS['groups']['group1'])
        self.assertTrue(_GLOBAL_SETTINGS['default'])

    def test_config_mode(self):
        """
        Verifies that the type checking mode can be configured
        """
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.invariant)
        config({'mode': None})
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.invariant)
        config({'mode': 'covariant'})
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.covariant)
        config({'mode': None})
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.covariant)
        config({'mode': 'invariant'})
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.invariant)
        config({'mode': None})
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.invariant)
        config({'mode': 'contravariant'})
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.contravariant)
        config({'mode': None})
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.contravariant)
        config({'mode': 'bivariant'})
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.bivariant)
        config({'mode': None})
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.bivariant)
        config(reset=True)
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.invariant)

        with self.assertRaises(KeyError):
            config({'mode': 'hello world'})

    def test_config_unknown_option(self):
        """
        Verifies that an unknown config option throws an exception
        """
        with self.assertRaises(KeyError):
            config({'hello_world': None})

    def test_config_altogether(self):
        """
        Verifies that different config options can work together
        """
        config_update = {
            'enabled': False,
            'groups': {
                    'set': {'group1': True, 'group2': False, 'group3': None},
                    'default': False,
                    'disable_previous': True,
                    'enable_previous': True,
                    'clear_previous': None
                },
            'mode': ModeChoices.bivariant.name
            }

        _GLOBAL_SETTINGS['groups']['group4'] = False

        config(config_update)

        self.assertFalse(_GLOBAL_SETTINGS['enabled'])
        self.assertEqual(len(_GLOBAL_SETTINGS['groups']), 3)
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group1'])
        self.assertFalse(_GLOBAL_SETTINGS['groups']['group2'])
        self.assertTrue(_GLOBAL_SETTINGS['groups']['group4'])
        self.assertFalse(_GLOBAL_SETTINGS['default'])
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.bivariant)

    def test_reset(self):
        """
        Verifies that config reset options sets changes the global settings to their default
        """
        config_update = {
            'enabled': False,
            'groups': {
                    'set': {'random': True},
                    'default': False
                },
            'mode': ModeChoices.bivariant.name
            }

        config(config_update)

        self.assertFalse(_GLOBAL_SETTINGS['enabled'])
        self.assertFalse(_GLOBAL_SETTINGS['default'])
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.bivariant)
        self.assertNotEqual(_GLOBAL_SETTINGS['groups'], {})

        config(reset=True)

        self.assertTrue(_GLOBAL_SETTINGS['enabled'])
        self.assertTrue(_GLOBAL_SETTINGS['default'])
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.invariant)
        self.assertEqual(_GLOBAL_SETTINGS['groups'], {})

        config(config_update, reset=True)

        self.assertTrue(_GLOBAL_SETTINGS['enabled'])
        self.assertTrue(_GLOBAL_SETTINGS['default'])
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.invariant)
        self.assertEqual(_GLOBAL_SETTINGS['groups'], {})

if __name__ == '__main__':
    unittest.main()
