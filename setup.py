from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='enforce',

    version='0.1.0',

    description='A simple Python project for enforcing runtime validation of function input and output data',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/RussBaz/enforce',

    # Author details
    author='R. Bazhenov',
    author_email='RussBaz@users.noreply.github.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='type validation',
    packages=['enforce']
)
