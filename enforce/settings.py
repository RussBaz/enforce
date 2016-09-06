import enum
import collections

from .utils import merge_dictionaries


class ModeChoices(enum.Enum):
    invariant = 0
    covariant = 1
    contravariant = 2
    bivariant = 3


class Settings:
    def __init__(self, enabled=None, group=None):
        self.group = group or 'default'
        self._enabled = enabled

    @property
    def enabled(self):
        """
        Returns if this instance of settings is enabled
        """
        if not _GLOBAL_SETTINGS['enabled']:
            return False

        if self._enabled is None:
            return _GLOBAL_SETTINGS['groups'].get(self.group, False)

        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

    def __bool__(self):
        return self.enabled


def config(options=None, *, reset=False):
    if reset:
        parsed_config = None
    else:
        parsed_config = parse_config(options)

    apply_config(parsed_config, reset)


def reset_config():
    _GLOBAL_SETTINGS['enabled'] = True
    _GLOBAL_SETTINGS['default'] = True
    _GLOBAL_SETTINGS['mode'] = ModeChoices.invariant
    _GLOBAL_SETTINGS['groups'] = {}


def parse_config(options):
    default_options = {
        'enabled': None,
        'groups': {
                'set': {},
                'disable_previous': False,
                'enable_previous': False,
                'clear_previous': False,
                'default': None
            },
        'mode': None
        }

    return merge_dictionaries(default_options, options)


def apply_config(options=None, reset=False):
    if reset:
        reset_config()
    elif options is not None:
        for key, value in options.items():
            if key == 'enabled':
                if value is not None:
                    _GLOBAL_SETTINGS['enabled'] = value
            elif key == 'groups':
                if value['disable_previous']:
                    for k in _GLOBAL_SETTINGS['groups']:
                        _GLOBAL_SETTINGS['groups'][k] = False

                if value['enable_previous']:
                    for k in _GLOBAL_SETTINGS['groups']:
                        _GLOBAL_SETTINGS['groups'][k] = True

                if value['clear_previous']:
                    for k in _GLOBAL_SETTINGS['groups']:
                        _GLOBAL_SETTINGS['groups'] = {}

                if value['default'] is not None:
                    _GLOBAL_SETTINGS['default'] = value['default']

                for k, v in value['set'].items():
                    if k == 'default':
                        raise KeyError('Cannot set \'default\' group status, use \'default\' option rather than \'set\'')
                    _GLOBAL_SETTINGS['groups'][k] = v
            elif key == 'mode':
                if value is not None:
                    try:
                        _GLOBAL_SETTINGS['mode'] = ModeChoices[value]
                    except KeyError:
                        raise KeyError('Mode must be one of mode choices')
            else:
                raise KeyError('Unknown option \'{}\''.format(key))


_GLOBAL_SETTINGS = {
    'enabled': True,
    'default': True,
    'mode': ModeChoices.invariant,
    'groups': {
        }
    }
