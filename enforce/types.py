import builtins
from collections import ChainMap
from typing import Optional, Union, Any, TypeVar


def is_type_of_type(data: Union[type, str],
               data_type: Union[type, str],
               covariant: bool=False,
               contravariant: bool=False,
               local_variables: Optional[dict] = None,
               global_variables: Optional[dict] = None
               ) -> bool:
    # Calling scope should be passed implicitly
    # Otherwise, it is assumed to be empty
    if local_variables is None:
        local_variables = {}

    if global_variables is None:
        global_variables = {}

    calling_scope = ChainMap(local_variables, global_variables, vars(builtins))

    # If a variable is string, then it should look it up in the scope of a calling function
    if isinstance(data_type, str):
        data_type = calling_scope[data_type]

    if isinstance(data, str):
        data = calling_scope[data]
    
    if covariant and contravariant:
        return (data_type in data.__mro__) or (data in data_type.__mro__)
    if covariant and not contravariant:
        return data_type in data.__mro__
    if not covariant and contravariant:
        return data in data_type.__mro__
    else:
        return data==data_type
