import builtins
import typing
import numbers
from collections import ChainMap
from typing import Optional, Union, Any, TypeVar, Tuple, Generic

# This enables a support for Python version 3.5.0-3.5.2
try:
    from typing import UnionMeta
except ImportError:
    UnionMeta = Union

from .utils import visit


class EnhancedTypeVar:
    """
    Utility wrapper for adding extra properties to default TypeVars
    Allows TypeVars to be bivariant
    Can be constructed as any other TypeVar or from existing TypeVars
    """

    def __init__(self,
                 name: str,
                 *constraints: Any,
                 bound: Optional[type] = None,
                 covariant: Optional[bool] = False,
                 contravariant: Optional[bool] = False,
                 type_var: Optional['TypeVar'] = None):
        if type_var is not None:
            self.__name__ = type_var.__name__
            self.__bound__ = type_var.__bound__
            self.__covariant__ = type_var.__covariant__
            self.__contravariant__ = type_var.__contravariant__
            self.__constraints__ = tuple(type_var.__constraints__)
        else:
            self.__name__ = name
            self.__bound__ = bound
            self.__covariant__ = covariant
            self.__contravariant__ = contravariant
            self.__constraints__ = tuple(constraints)
            if len(self.__constraints__) == 1:
                raise TypeError('A single constraint is not allowed')

    @property
    def constraints(self):
        """
        Returns constrains further constrained by the __bound__ value
        """
        if self.__bound__:
            return (self.__bound__, )
        else:
            return self.__constraints__

    def __eq__(self, data):
        """
        Allows comparing Enhanced Type Var to other type variables (enhanced or not)
        """
        name = getattr(data, '__name__', None) == self.__name__
        bound = getattr(data, '__bound__', None) == self.__bound__
        covariant = getattr(data, '__covariant__', None) == self.__covariant__
        contravariant = getattr(data, '__contravariant__', None) == self.__contravariant__
        constraints = getattr(data, '__constraints__', None) == self.__constraints__
        return all((name, bound, covariant, contravariant, constraints))

    def __hash__(self):
        """
        Provides hashing for use in dictionaries
        """
        name = hash(self.__name__)
        bound = hash(self.__bound__)
        covariant = hash(self.__covariant__)
        contravariant = hash(self.__contravariant__)
        constraints = hash(self.__constraints__)

        return name ^ bound ^ covariant ^ contravariant ^ constraints

    def __repr__(self):
        """
        Further enhances TypeVar representation through addition of bi-variant symbol
        """
        if self.__covariant__ and self.__contravariant__:
            prefix = '*'
        elif self.__covariant__:
            prefix = '+'
        elif self.__contravariant__:
            prefix = '-'
        else:
            prefix = '~'
        return prefix + self.__name__


# According to https://docs.python.org/3/reference/datamodel.html,
# there are two types of integers - int and bool, but the 'PEP 3141 -- A Type Hierarchy for Numbers'
# (https://www.python.org/dev/peps/pep-3141/)
# makes no such distinction.
# As I could not find required base classes to differentiate between two types of integers,
# I decided to add my own classes.
# If I am wrong, please let me know


class Integer(numbers.Integral):
    """
    Integer stub class
    """
    pass


class Boolean(numbers.Integral):
    """
    Boolean stub class
    """
    pass


TYPE_ALIASES = {
    tuple: Tuple,
    int: Integer,
    bool: Boolean,
    float: numbers.Real,
    complex: numbers.Complex,
    dict: typing.Dict,
    list: typing.List,
    set: typing.Set,
    None: type(None)
}


REVERSED_TYPE_ALIASES = {v: k for k, v in TYPE_ALIASES.items()}


# Tells the type checking method to ignore __subclasscheck__
# on the following types and their subclasses
IGNORED_SUBCLASSCHECKS = [
    Generic
]


def is_type_of_type(data: Union[type, str, None],
                    data_type: Union[type, str, 'TypeVar', EnhancedTypeVar, None],
                    covariant: bool = False,
                    contravariant: bool = False,
                    local_variables: Optional[typing.Dict]=None,
                    global_variables: Optional[typing.Dict]=None
                   ) -> bool:
    """
    Returns if the type or type like object is of the same type as constrained
    Support co-variance, contra-variance and TypeVar-s
    Also, can extract type from the scope if only its name was given
    """
    # Calling scope should be passed implicitly
    # Otherwise, it is assumed to be empty
    if local_variables is None:
        local_variables = {}

    if global_variables is None:
        global_variables = {}

    calling_scope = ChainMap(local_variables, global_variables, vars(typing), vars(builtins))

    # If a variable is string, then it should look it up in the scope of a calling function
    if isinstance(data_type, str):
        data_type = calling_scope[data_type]

    if isinstance(data, str):
        data = calling_scope[data]

    data_type = visit(sort_and_flat_type(data_type))
    data = visit(sort_and_flat_type(data))

    subclasscheck_enabled = True
    is_type_var = data_type.__class__ is TypeVar or data_type.__class__ is EnhancedTypeVar

    # TypeVars have a list of constraints and it can be bound to a specific constraint (which takes precedence)
    if is_type_var:
        if data_type.__bound__:
            constraints = [data_type.__bound__]
        else:
            constraints = data_type.__constraints__
        # TypeVars ignore original covariant and contravariant options
        # They always use their own
        covariant = data_type.__covariant__
        contravariant = data_type.__contravariant__
    elif data_type is Any:
        constraints = [Any]
    elif str(data_type).startswith('typing.Union'):
        constraints = [data_type]
    else:
        subclasscheck_enabled = not any(data_type.__class__ is t or t in data_type.__mro__ for t in IGNORED_SUBCLASSCHECKS)
        constraints = [data_type]

    if not constraints:
        constraints = [Any]

    constraints = [TYPE_ALIASES.get(constraint, constraint) for constraint in constraints]

    if Any in constraints:
        return True
    else:
        if not covariant and not contravariant:
            return any(data == d for d in constraints)
        else:
            subclass_check = None

            if not is_type_var and subclasscheck_enabled:
                subclass_check = perform_subclasscheck(data, data_type, covariant, contravariant)

            if subclass_check is not None:
                return subclass_check

            if covariant and contravariant:
                return any((d in data.__mro__) or (data in d.__mro__) for d in constraints)

            if covariant:
                return any(d in data.__mro__ for d in constraints)

            if contravariant:
                return any(data in d.__mro__ for d in constraints)


def perform_subclasscheck(data, data_type, covariant, contravariant):
    """
    Calls a __subclasscheck__ method with provided types according to the covariant and contravariant property

    Also, if a type is type alias, it tries to call its original version in case of subclass check failure
    """
    results = []

    if covariant:
        reversed_data = REVERSED_TYPE_ALIASES.get(data, data)
        result = data_type.__subclasscheck__(data)

        if data is not reversed_data:
            if reversed_data is None: reversed_data = type(None)
            result = result or data_type.__subclasscheck__(reversed_data)

        if result != NotImplemented:
            results.append(result)

    if contravariant:
        reversed_data_type = REVERSED_TYPE_ALIASES.get(data_type, data_type)
        result = data.__subclasscheck__(data_type)

        if data_type is not reversed_data_type:
            if reversed_data_type is None: reversed_data_type = type(None)
            result = result or data.__subclasscheck__(reversed_data_type)

        if result != NotImplemented:
            results.append(result)

    if any(results):
        return True

    if not all(results):
        return False

    return None


def sort_and_flat_type(type_in):
    """
    Recursively sorts Union and TypeVar constraints in alphabetical order
    and replaces type aliases with their ABC counterparts
    """
    # Checks if the type is in the list of type aliases
    # And replaces it (if found) with a base form
    try:
        type_in = TYPE_ALIASES.get(type_in, type_in)
    except TypeError:
        pass

    if type_in.__class__ is UnionMeta:
        nested_types_in = type_in.__union_params__
        nested_types_out = []
        for t in nested_types_in:
            t = yield sort_and_flat_type(t)
            nested_types_out.append(t)
        nested_types_out = sorted(nested_types_out, key=repr)
        type_out = Union[tuple(nested_types_out)]
    elif type_in.__class__ is TypeVar or type_in.__class__ is EnhancedTypeVar:
        nested_types_in = type_in.__constraints__
        nested_types_out = []
        for t in nested_types_in:
            t = yield sort_and_flat_type(t)
            nested_types_out.append(t)
        nested_types_out = sorted(nested_types_out, key=repr)
        type_out = EnhancedTypeVar(type_in.__name__, type_var=type_in)
        type_out.__constraints__ = nested_types_out
    else:
        type_out = type_in

    yield type_out


def is_named_tuple(data):
    try:
        fields = data._fields
        field_types = getattr(data, '_field_types', {})

        if type(data) == type:
            data_type = data
        else:
            data_type = type(data)

            if len(fields) != len(data):
                return False

        is_tuple = is_type_of_type(data_type, tuple, covariant=True)

        if not is_tuple:
            return False

        for field_name in field_types.keys():
            if field_name not in fields:
                return False

        for field_name in fields:
            getattr(data, field_name)

    except (AttributeError, TypeError):
        return False

    else:
        return True
