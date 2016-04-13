import typing
from collections import UserList, MutableSequence

from wrapt import ObjectProxy


class Proxy(ObjectProxy):
    """
    Transparent proxy with an option of attributes being saved on the proxy instance.
    """
    
    def __init__(self, wrapped):
        """
        By default, it acts as a transparent proxy
        """
        super().__init__(wrapped)
        self.pass_through = True

    def __setattr__(self, name, value):
        """
        Saves attribute on the proxy with a '_self_' prefix
        if '_self_pass_through' is NOT defined
        Otherwise, it is saved on the wrapped object
        """
        if hasattr(self, '_self_pass_through'):
            return super().__setattr__(name, value)

        return super().__setattr__('_self_'+name, value)

    def __getattr__(self, name):
        if name == '__wrapped__':
            raise ValueError('wrapper has not been initialised')
        
        # Clever thing - this prevents infinite recursion when this
        # attribute is not defined
        if name == '_self_pass_through':
            raise AttributeError()

        if hasattr(self, '_self_pass_through'):
            return getattr(self.__wrapped__, name)
        else:
            # Attempts to return a local copy if such attribute exists
            # on the wrapped object but falls back to default behaviour
            # if there is no local copy, i.e. attribute with '_self_' prefix
            if hasattr(self.__wrapped__, name):
                try:
                    return getattr(self, '_self_'+name)
                except AttributeError:
                    pass
            return getattr(self.__wrapped__, name)

    @property
    def pass_through(self):
        """
        Returns if the proxy is transparent or can save attributes on itself
        """
        return hasattr(self._self_pass_through)

    @pass_through.setter
    def pass_through(self, full_proxy):
        if full_proxy:
            self._self_pass_through = None
        else:
            del(self._self_pass_through)


class ListProxy(ObjectProxy):
    def __init__(self, input_validators: typing.List, output_validators: typing.List, wrapped: typing.List) -> None:
        self._self_input_validators = input_validators
        self._self_output_validators = output_validators
        super().__init__(wrapped)
    def __repr__(self): return self.__wrapped__.__repr__()
    def __lt__(self, other): return self.__wrapped__.__lt__(other)
    def __le__(self, other): return self.__wrapped__.__le__(other)
    def __eq__(self, other): return self.__wrapped__.__eq__(other)
    def __gt__(self, other): return self.__wrapped__.__gt__(other)
    def __ge__(self, other): return self.__wrapped__.__ge__(other)
    def __contains__(self, item): return self.__wrapped__.__contains__(item)
    def __len__(self): return self.__wrapped__.__len__()
    def __getitem__(self, i): return self.__wrapped__.__getitem__(i)
    def __setitem__(self, i, item): return self.__wrapped__.__setitem__(i, item)
    def __delitem__(self, i): return self.__wrapped__.__delitem__(i)
    def __add__(self, other): return self.__wrapped__.__add__(other)
    def __radd__(self, other): return self.__wrapped__.__radd__(other)
    def __iadd__(self, other): return self.__wrapped__.__iadd__(other)
    def __mul__(self, n): return self.__wrapped__.__mul__(n)
    __rmul__ = __mul__
    def __imul__(self, n): return self.__wrapped__.__imul__(n)

    def append(self, item): self.__wrapped__.append(item)
    def insert(self, i, item): self.__wrapped__.insert(i, item)
    def pop(self, i=-1): return self.__wrapped__.pop(i)
    def remove(self, item): self.__wrapped__.remove(item)
    def clear(self): self.__wrapped__.clear()
    def copy(self): return self.__wrapped__.copy()
    def count(self, item): return self.__wrapped__.count(item)
    def index(self, item, *args): return self.__wrapped__.index(item, *args)
    def reverse(self): self.__wrapped__.reverse()
    def sort(self, *args, **kwds): self.__wrapped__.sort(*args, **kwds)
    def extend(self, other): self.__wrapped__.extend(other)
