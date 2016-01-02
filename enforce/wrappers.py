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
