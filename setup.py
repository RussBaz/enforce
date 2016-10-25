from os import path
import codecs
from setuptools import setup

ROOT = path.abspath(path.dirname(__file__))

with codecs.open(path.join(ROOT, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = ''.join(f.readlines())

setup(
    name='enforce',

    version='0.3.2',

    description='Python 3.5+ library for integration testing and data validation through configurable and optional runtime type hint enforcement.',
    long_description=LONG_DESCRIPTION,

    url='https://github.com/RussBaz/enforce',
    author='RussBaz',
    author_email='RussBaz@users.noreply.github.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='type validation type hints runtime type checking',
    packages=['enforce'],
    install_requires=[
        'wrapt'
    ]
)
