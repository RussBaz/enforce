import typing

from wrapt import CallableObjectProxy, ObjectProxy

from .exceptions import RuntimeTypeError


class Proxy(CallableObjectProxy):
    """
    Transparent proxy with an option of attributes being saved on the proxy instance.
    """
    
    def __init__(self, wrapped):
        """
        By default, it acts as a transparent proxy
        """
        self._self_pass_through = True
        super().__init__(wrapped)

    def __setattr__(self, name, value):
        """
        Saves attribute on the proxy with a '_self_' prefix
        if '_self_pass_through' is NOT defined
        Otherwise, it is saved on the wrapped object
        """
        if hasattr(self, '_self_pass_through'):
            return object.__setattr__(self.__wrapped__, name, value)

        return object.__setattr__(self, '_self_'+name, value)

    def __getattr__(self, name):
        if name == '__wrapped__':
            raise ValueError('wrapper has not been initialised')
        
        # Clever thing - this prevents infinite recursion when this
        # attribute is not defined
        if name == '_self_pass_through':
            raise AttributeError()

        if hasattr(self, '_self_pass_through'):
            return super().__getattr__(name)
        else:
            # Attempts to return a local copy if such attribute exists
            # on the wrapped object but falls back to default behaviour
            # if there is no local copy, i.e. attribute with '_self_' prefix
            try:
                return super().__getattr__('_self_'+name)
            except AttributeError:
                return super().__getattr__(name)

    @property
    def pass_through(self):
        """
        Returns if the proxy is transparent or can save attributes on itself
        """
        return self._self_pass_through

    @pass_through.setter
    def pass_through(self, full_proxy):
        if full_proxy:
            self._self_pass_through = True
        else:
            self._self_pass_through = False


class EnforceProxy(ObjectProxy):
    """
    A proxy object for safe addition of runtime type enforcement without mutating the original object
    """
    def __init__(self, wrapped, enforcer=None):
        super().__init__(wrapped)
        self._self_enforcer = enforcer

    @property
    def __enforcer__(self):
        return self._self_enforcer

    @__enforcer__.setter
    def __enforcer__(self, value):
        self._self_enforcer = value

    def __call__(self, *args, **kwargs):
        if type(self.__wrapped__) is type:
            return EnforceProxy(self.__wrapped__(*args, **kwargs), self.__enforcer__)
        return self.__wrapped__(*args, **kwargs)


#class ListProxy(ObjectProxy):
#    # Convention: List input parameter is called 'item'

#    def __init__(self, wrapped: typing.List, validator: typing.Optional['Validator']=None) -> None:
#        self._self_validator = validator
#        super().__init__(wrapped)

#    def __contains__(self, item):
#        func = lambda: self.__wrapped__.__contains__(item)
#        return self.__clean_input(item, func)

#    def __getitem__(self, i):
#        return self.__clean_output(lambda: self.__wrapped__.__getitem__(i))

#    def __setitem__(self, i, item):
#        func = lambda: self.__wrapped__.__setitem__(i, item)
#        return self.__clean_input(item, func)

#    def __delitem__(self, i):
#        return self.__wrapped__.__delitem__(i)
    
#    def __add__(self, other):
#        return self.__wrapped__.__add__(other)
#    def __radd__(self, other): return self.__wrapped__.__radd__(other)
#    def __iadd__(self, other): return self.__wrapped__.__iadd__(other)

#    def append(self, item): self.__wrapped__.append(item)
#    def insert(self, i, item): self.__wrapped__.insert(i, item)

#    def pop(self, i=-1): return self.__wrapped__.pop(i)
#    def remove(self, item): self.__wrapped__.remove(item)

#    def count(self, item): return self.__wrapped__.count(item)
#    def index(self, item, *args): return self.__wrapped__.index(item, *args)

#    def extend(self, other): self.__wrapped__.extend(other)

#    def __clean_input(self, item: typing.Any, func: typing.Callable):
#        try:
#            if self._self_validator.validate(item, 'item'):
#                return func()
#            else:
#                raise RuntimeTypeError('Unsupported input type')
#        except AttributeError:
#            return func()

#    def __clean_output(self, func: typing.Callable):
#        result = func()
#        try:
#            if not self._self_validator.validate(result, 'return'):
#                raise RuntimeTypeError('Unsupported return type')
#        except AttributeError:
#            pass
#        return result
