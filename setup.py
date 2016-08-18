from os import path
import codecs
from setuptools import setup

ROOT = path.abspath(path.dirname(__file__))

with codecs.open(path.join(ROOT, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='enforce',

    version='0.2.0',

    description='A Python library for enforcing runtime validation of function inputs and outputs',
    long_description=LONG_DESCRIPTION,

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
    packages=['enforce'],
    install_requires=[
          'wrapt',
    ]
)
