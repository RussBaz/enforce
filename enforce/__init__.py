from .decorators import runtime_validation
from .exceptions import EnforceConfigurationError


class Config(object):
    def __init__(self, global_config=None):
        if global_config is None:
            self.recursion_limit = -1
            self.iterable_size = 'all'
            self.group = 'main'
            self.enable = True
            self.groups = {}
        else:
            self.parent = global_config

    def __getattribute__(self, item):
        """
        We override this to have values default to global singleton unless set by user
        """
        try:
            value = object.__getattribute__(self, item)
        except AttributeError:
            value = object.__getattribute__(self.parent, item)
        return value

    def __str__(self):
        return str(self.__dict__)

    def __bool__(self):
        if self.group in self.parent.groups.keys():
            return self.parent.groups[self.group]
        return self.enable

    def set(self, **kwargs):
        config(configuration=self, **kwargs)


""" Global config is singleton """
user_configuration = Config()


def config(configuration=None, **kwargs):
    if configuration is None:
        configuration= user_configuration
    for key, value in kwargs.items():
        if (key == 'recursion_limit') and ((type(value) is not int) or (value < -1)):
                raise EnforceConfigurationError
        if (key == 'iterable_size') and (value not in ['none', 'first', 'all']):
                raise EnforceConfigurationError
        if (key == 'group') and (type(value) is not str):
                raise EnforceConfigurationError
        if (key == 'enable') and (value not in [False, True]):
                raise EnforceConfigurationError
        configuration.__dict__[key] = value


def set_group(group_name, status):
    if status not in [True, False]:
        raise EnforceConfigurationError
    user_configuration.groups[group_name] = status
