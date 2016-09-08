import typing
from copy import deepcopy


def visit(generator):
    """
    Runs ('visits') the provided generator till completion
    Returns the last yielded value
    Avoids recursion by using stack
    """
    stack = [generator]
    last_result = None
    while stack:
        try:
            last = stack[-1]
            if isinstance(last, typing.Generator):
                stack.append(last.send(last_result))
                last_result = None
            else:
                last_result = stack.pop()
        except StopIteration:
            stack.pop()

    return last_result


def merge_dictionaries(original_data, update, merge_lists=False):
    """
    Recursively merges values of two dictionaries
    """
    merged_data = deepcopy(original_data)

    for key, value in update.items():
        if isinstance(value, dict):
            merged_data[key] = merge_dictionaries(merged_data.get(key, {}), value)
        elif merge_lists and isinstance(merged_data.get(key), list) and isinstance(value, list):
            merged_data[key] = merged_data[key] + value
        else:
            merged_data[key] = value

    return merged_data
