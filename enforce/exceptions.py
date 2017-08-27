import typing


class RuntimeTypeError(Exception):
    pass


def parse_errors(errors: typing.List[typing.Tuple[str, str]], hints: typing.Dict[str, type], return_type: bool=False) -> str:
    """
    Generates an exception message based on which fields failed
    """
    error_message = "       Argument '{0}' was not of type {1}. Actual type was {2}."
    return_error_message = "        Return value was not of type {0}. Actual type was {1}."
    output = "\n  The following runtime type errors were encountered:"

    for error in errors:
        argument_name, argument_type = error
        hint = hints.get(argument_name, type(None))
        if return_type:
            output += '\n' + return_error_message.format(hint, argument_type)
        else:
            output += '\n' + error_message.format(argument_name, hint, argument_type)
    return output


def raise_errors(exception, message):
    raise exception(message)


def process_errors(parser, exception, errors, hints, is_return_type=False):
    message = parser(errors, hints, is_return_type)
    raise_errors(exception, message)
