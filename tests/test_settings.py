import unittest

from enforce.settings import Settings, _GLOBAL_SETTINGS, ModeChoices, config


class SettingsTests(unittest.TestCase):

    def setUp(self):
        _GLOBAL_SETTINGS['enabled'] = True
        _GLOBAL_SETTINGS['default'] = True
        _GLOBAL_SETTINGS['mode'] = ModeChoices.invariant
        _GLOBAL_SETTINGS['groups'] = {}

    def test_reset(self):
        """
        Verifies that config reset options sets changes the global settings to their default
        """
        config({
            'enabled': False,
            'groups': {
                    'set': {'random': True},
                    'default': False
                },
            'mode': ModeChoices.bivariant.name
            })

        config(reset=True)

        self.assertTrue(_GLOBAL_SETTINGS['enabled'])
        self.assertTrue(_GLOBAL_SETTINGS['default'])
        self.assertEqual(_GLOBAL_SETTINGS['mode'], ModeChoices.invariant)
        self.assertEqual(_GLOBAL_SETTINGS['groups'], {})

if __name__ == '__main__':
    unittest.main()
