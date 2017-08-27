import enum
import inspect

from .exceptions import parse_errors, process_errors

from .utils import merge_dictionaries


class ModeChoices(enum.Enum):
    """
    All possible values for the type checking mode
    """
    invariant = 0
    covariant = 1
    contravariant = 2
    bivariant = 3


class ErrorSettings:
    @property
    def parser(self):
        return _GLOBAL_SETTINGS['errors']['parser']

    @property
    def processor(self):
        return _GLOBAL_SETTINGS['errors']['processor']


class Settings:
    def __init__(self, enabled=None, group=None):
        self.group = group or 'default'
        self._enabled = enabled
        self._error_settings = ErrorSettings()

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
        """
        Only changes the local enabled
        """
        self._enabled = value

    @property
    def mode(self):
        """
        Returns currently selected type checking mode
        If it is None, then it will return invariant
        """
        return _GLOBAL_SETTINGS['mode'] or ModeChoices.invariant

    @property
    def covariant(self):
        """
        Returns if covariant type checking mode is enabled
        """
        return _GLOBAL_SETTINGS['mode'] in (ModeChoices.covariant, ModeChoices.bivariant)

    @property
    def contravariant(self):
        """
        Returns if contravariant type checking mode is enabled
        """
        return _GLOBAL_SETTINGS['mode'] in (ModeChoices.contravariant, ModeChoices.bivariant)

    @property
    def errors(self):
        """
        Returns error settings
        """
        return self._error_settings

    def __bool__(self):
        return bool(self.enabled)


def config(options=None, *, reset=False):
    """
    Starts the config update based on the provided dictionary of Options
    'None' value indicates no changes will be made
    """
    if reset:
        parsed_config = None
    else:
        parsed_config = parse_config(options)

    apply_config(parsed_config, reset)


def reset_config():
    """
    Resets the global config object to its original state
    """
    default_values = {
        'enabled': True,
        'default': True,
        'mode': ModeChoices.invariant,
        'groups': None,
        'errors': {
            'parser': parse_errors,
            'processor': process_errors
        }
    }

    keys_to_remove = []

    for key in _GLOBAL_SETTINGS:
        if key not in default_values:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del _GLOBAL_SETTINGS[key]

    for key, value in default_values.items():
        if value is not None:
            _GLOBAL_SETTINGS[key] = value

    _GLOBAL_SETTINGS['groups'].clear()


def parse_config(options):
    """
    Updates the default config update with a new values for config update
    """
    default_options = {
        'enabled': None,
        'groups': {
            'set': {},
            'disable_previous': False,
            'enable_previous': False,
            'clear_previous': False,
            'default': None
            },
        'mode': None,
        'errors': {
            'parser': None,
            'processor': None
        }
        }

    return merge_dictionaries(default_options, options)


def apply_config(options=None, reset=False):
    """
    Modifies the global settings object with a provided config updates
    """
    if reset:
        reset_config()
    elif options is not None:
        for key, value in options.items():
            if key == 'enabled':
                if value is not None:
                    _GLOBAL_SETTINGS['enabled'] = value

            elif key == 'groups':
                # For x_previous options, the priority is as follows:
                # 1. Clear
                # 2. Enable
                # 3. Disable

                group_update = {}
                previous_update = []

                for k, v in value.items():
                    if k == 'disable_previous':
                        if v:
                            previous_update.append('d')

                    elif k == 'enable_previous':
                        if v:
                            previous_update.append('e')

                    elif k == 'clear_previous':
                        if v:
                            previous_update.append('c')

                    elif k == 'default':
                        if v is not None:
                            _GLOBAL_SETTINGS['default'] = value['default']

                    elif k == 'set':
                        for group_name, group_status in v.items():
                            if group_name == 'default':
                                raise KeyError('Cannot set \'default\' group status, use \'default\' option rather than \'set\'')
                            if group_status is not None:
                                group_update[group_name] = group_status

                    else:
                        raise KeyError('Unknown option for groups \'{}\''.format(k))
                
                if previous_update:
                    if 'd' in previous_update:
                        for group_name in _GLOBAL_SETTINGS['groups']:
                            _GLOBAL_SETTINGS['groups'][group_name] = False

                    if 'e' in previous_update:
                        for group_name in _GLOBAL_SETTINGS['groups']:
                            _GLOBAL_SETTINGS['groups'][group_name] = True

                    if 'c' in previous_update:
                        _GLOBAL_SETTINGS['groups'].clear()

                _GLOBAL_SETTINGS['groups'].update(group_update)

            elif key == 'mode':
                if value is not None:
                    try:
                        _GLOBAL_SETTINGS['mode'] = ModeChoices[value]
                    except KeyError:
                        raise KeyError('Mode must be one of mode choices')
            elif key == 'errors':
                error_handling_update = {}

                if value is not None:
                    for k, v in value.items():
                        if k in ('parser', 'processor'):
                            if v is None:
                                error_handling_update.pop(k, None)
                            elif not inspect.isfunction(v):
                                raise KeyError('Error parser is not a function')
                            else:
                                error_handling_update[k] = v
                        else:
                            raise KeyError('Unknown option for errors: \'{}\''.format(k))

                    _GLOBAL_SETTINGS['errors'].update(error_handling_update)
            else:
                raise KeyError('Unknown option \'{}\''.format(key))


_GLOBAL_SETTINGS = {
    'enabled': True,
    'default': True,
    'mode': ModeChoices.invariant,
    'groups': {},
    'errors': {
        'parser': parse_errors,
        'processor': process_errors
    }
}
