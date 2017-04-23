|  Branch	| Status  |
| :-------:	| :--- 	  |
|  Master: 	| [![Build Status](https://img.shields.io/travis/RussBaz/enforce/master.svg)](https://travis-ci.org/RussBaz/enforce) [![Appveyor Build Status](https://ci.appveyor.com/api/projects/status/github/RussBaz/enforce?branch=master&svg=true)](https://ci.appveyor.com/project/RussBaz/enforce) [![Coverage Status](https://img.shields.io/coveralls/RussBaz/enforce/master.svg)](https://coveralls.io/github/RussBaz/enforce?branch=master) [![Requirements Status](https://img.shields.io/requires/github/RussBaz/enforce/master.svg)](https://requires.io/github/RussBaz/enforce/requirements/?branch=master) [![PyPI version](https://img.shields.io/pypi/v/enforce.svg)](https://pypi.python.org/pypi/enforce)	|
|   Dev:  	| [![Build Status](https://img.shields.io/travis/RussBaz/enforce/dev.svg)](https://travis-ci.org/RussBaz/enforce) [![Appveyor Build Status](https://ci.appveyor.com/api/projects/status/github/RussBaz/enforce?branch=dev&svg=true)](https://ci.appveyor.com/project/RussBaz/enforce) [![Coverage Status](https://img.shields.io/coveralls/RussBaz/enforce/dev.svg)](https://coveralls.io/github/RussBaz/enforce?branch=dev) [![Requirements Status](https://img.shields.io/requires/github/RussBaz/enforce/dev.svg)](https://requires.io/github/RussBaz/enforce/requirements/?branch=dev)	|

# Enforce.py

*__Enforce.py__* is a Python 3.5+ library for integration testing and data validation through configurable and optional runtime type hint enforcement. It uses the standard type hinting syntax (defined in PEP 484).

**NOTICE:** Python versions 3.5.2 and earlier (3.5.0-3.5.2) are now deprecated. Only Python versions 3.5.3+ would be supported. Deprecated versions will no longer be officially supported in Enforce.py version 0.4.x.

* [Overview](#overview)
* [Installation](#installation)
* [Usage](#usage)
  * [Features](#features)
    * [Basics](#basic-type-hint-enforcement)
    * [Callable](#callable-support)
    * [TypeVar and Generics](#typevar-and-generics)
    * [Class Decorator](#class-decorator)
    * [NamedTuple](#namedtuple)
  * [Configuration](#configuration)
* [Changelog](#changelog)
* [Contributing](#contributing)

## Overview

* Supports most of simple and nested types
* Supports Callables, TypeVars and Generics
* Supports invariant, covariant, contravariant and bivariant type checking
  * **Default** mode is *__invariant__*
* Can be applied to both functions and classes (in this case it will be applied to all methods of the class)
* Highly configurable
  * Global on/off switch
  * Group configuration
  * Local override of groups
  * Type checking mode selection
  * Dynamic reconfiguration

## Installation

Stable 0.3.x - Stable and ready for every day use version

    pip install enforce

Dev current - "Bleeding edge" features that, while are fairly consistent, may
change.

    pip install git+https://github.com/RussBaz/enforce.git@dev

## Usage

Type enforcement is done using decorators around functions that you desire to be
checked. By default, this decorator will ensure that any variables passed into
the function call matches its declaration (invariantly by default). This includes integers, strings, etc.
as well as lists, dictionaries, and more complex objects. Currently, the type checking is eager.

Note, eager means that for a large nested structure, every item in that
structure will be checked. This may be a nightmare for performance! See
[caveats](#caveats) for more details.

You can also apply the `runtime_validation` decorator around a class, and it
will enforce the types of every method in that class.

**Note:** this is a development feature and is not as thoroughly tested as the function decorators.

### Features

#### Basic type hint enforcement

```python
>>> import enforce
>>>
>>> @enforce.runtime_validation
... def foo(text: str) -> None:
...     print(text)
>>>
>>> foo('Hello World')
Hello World
>>>
>>> foo(5)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/william/.local/lib/python3.5/site-packages/enforce/decorators.py", line 106, in universal
    _args, _kwargs = enforcer.validate_inputs(parameters)
  File "/home/william/.local/lib/python3.5/site-packages/enforce/enforcers.py", line 69, in validate_inputs
    raise RuntimeTypeError(exception_text)
enforce.exceptions.RuntimeTypeError: 
  The following runtime type errors were encountered:
       Argument 'text' was not of type <class 'str'>. Actual type was <class 'int'>.
>>>
```

#### Callable Support

```python
@runtime_validation
def foo(a: typing.Callable[[int, int], str]) -> str:
    return a(5, 6)

def bar(a: int, b: int) -> str:
    return str(a * b)

class Baz:
    def __call__(self, a: int, b: int) -> str:
      return bar(a, b)

foo(bar)
foo(Baz())
```

#### TypeVar and Generics

```python
T = typing.TypeVar('T', int, str)

@runtime_validation
class Sample(typing.Generic[T]):
    def get(self, data: T) -> T:
        return data

@runtime_validation
def foo(data: Sample[int], arg: int) -> int:
    return data.get(arg)

@runtime_validation
def bar(data: T, arg: int) -> T:
    return arg

sample_good = Sample[int]()
sample_bad = Sample()

with self.assertRaises(TypeError):
    sample = Sample[list]()

foo(sample_good, 1)

with self.assertRaises(RuntimeTypeError):
    foo(sample_bad, 1)

bar(1, 1)

with self.assertRaises(RuntimeTypeError):
    bar('str', 1)
```

#### Class Decorator

Applying this decorator to a class will automatically apply the decorator to
every method in the class.

```python
@runtime_validation
class DoTheThing(object):
    def __init__(self):
        self.do_the_stuff(5, 6.0)

    def do_the_stuff(self, a: int, b: float) -> str:
        return str(a * b)
```

#### NamedTuple

Enforce.py supports typed NamedTuples.

```python
MyNamedTuple = typing.NamedTuple('MyNamedTuple', [('param', int)])

# Optionally making a NamedTuple typed
# It will now enforce its type signature
# and will throw exceptions if there is a type mismatch
# MyNamedTuple(param='str') will now throw an exception
MyNamedTuple = runtime_validation(MyNamedTuple)

# This function now accepts only NamedTuple arguments
@runtime_validation
def foo(data: MyNamedTuple):
    return data.param
```

### Configuration

You can assign functions to groups, and apply options on the group level.

'None' leaves previous value unchanged.

All available global settings:
```python
default_options = {
    # Global enforce.py on/off switch
    'enabled': None,
    # Group related settings
    'groups': {
        # Dictionary of type {<name: str>: <status: bool>}
		# Sets the status of specified groups
		# Enable - True, disabled - False, do not change - None
        'set': {},
		# Sets the status of all groups to False before updating
        'disable_previous': False,
		# Sets the status of all groups to True before updating
        'enable_previous': False,
        # Deletes all the existing groups before updating
        'clear_previous': False,
		# Updating the default group status - default group is not affected by other settings
        'default': None
    },
    # Sets the type checking mode
    # Available options: 'invariant', 'covariant', 'contravariant', 'bivariant' and None
    'mode': None
    }
```

```python
# Basic Example
@runtime_validation(group='best_group')
def foo(a: List[str]):
    pass

foo(1)	# No exception as the 'best_group' was not explicitly enabled
    
# Group Configuration
enforce.config({'groups': {'set': {'best_group': True}}}) # Enabling group 'best_group'

with self.assertRaises(RuntimeTypeError):
    foo(1)

enforce.config({
    'groups': {
        'set': {
            'foo': True
            },
        'disable_previous': True,
        'default': False
        }
    })  # Disable everything but the 'foo' group

# Using foo's settings
@runtime_validation(group='foo')
def test1(a: str): return a

# Using foo's settings but locally overriding it to stay constantly enabled
@runtime_validation(group='foo', enabled=False)
def test2(a: str): return a

# Using bar's settings - deactivated group -> no type checking is performed
@runtime_validation(group='bar')
def test3(a: str): return a

# Using bar's settings but overriding locally -> type checking enabled
@runtime_validation(group='bar', enabled=True)
def test4(a: str): return a

with self.assertRaises(RuntimeTypeError):
    test1(1)
test2(1)
test3(1)
with self.assertRaises(RuntimeTypeError):
    test4(1)

foo(1)

enforce.config({'enabled': False})  # Disables enforce.py

test1(1)
test2(1)
test3(1)
test4(1)
foo(1)

enforce.config({'enabled': True})  # Re-enables enforce.py

enforce.config(reset=True) # Resets global settings to their default state
```

### Caveats

Currently, iterators, generators and coroutines type checks are not supported (mostly).
However, it is still possible to check if an object is iterable.

We are still working on the best approach for lazy type checking (checking list items only when accessed)
and lazy type evaluation (accepting strings as type hints).

Currently, the type checker will examine every object in a list. This means that
for large structures performance can be a nightmare.

Class decorators are not as well tested, and you may encounter a bug or two.
Please report an issue if you do find one and we'll try to fix it as quickly as
possible.

## Changelog

### 0.3.3 - 23.04.2017

* Improved support for Dictionaries
* Fixed some thread safety issues

### 0.3.2 - 29.01.2017

* Added support for Python 3.5.3 and 3.6.0
* Added support for NamedTuple
* Added support for Set
* New exception message generation system
* Fixed failing nested lists type checking

### 0.3.1 - 17.09.2016

* Added support for Callable classes (classes with \_\_call\_\_ method are now treated like any other Callable object)
* Fixed bugs in processing callables without specified return type

## Contributing

Please check out our active issues on our Github page to see what work needs to
be done, and feel free to create a new issue if you find a bug.

Actual development is done in the 'dev' branch, which is merged to master at
milestones.
