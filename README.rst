Enforce is a simple Python 3.5 (or higher) application for enforcing a runtime type checking based on type hints (PEP 484).

This project is not yet ready for production but we will be happy if you give it a try.

Actual development is done in the 'dev' branch.

Installation:

(stable 0.1)

    pip install enforce
   
   
(dev current)

    pip install git+https://github.com/RussBaz/enforce.git
  

Usage Examples:

.. code:: python

    import enforce
   
    @enforce.runtime_validation
    def foo(text: str) -> None:
        print(text)
       
Also, you can deactivate at runtime all 'enforcers', each one of them individually or as a group (using 'group' tags).

ATTENTION, this functionality is still under development and its syntax may change at any time.

Generics and containers are NOT yet supported. Callables and TypeVars should be generally supported.
