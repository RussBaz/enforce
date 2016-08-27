import typing


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
