Enforce is a simple Python 3.5 or higher application for enforcing a runtime type checking based on type hints.

Installation:

    pip install enforce

Usage Examples:

.. code:: python

    import enforce
    
    @enforce.runtime_validation
    def foo(text: str) -> None:
        print(text)