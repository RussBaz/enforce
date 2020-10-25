import warnings
from pathlib import Path

from setuptools import setup

try:
    import pypandoc

    PYPANDOC_EXISTS = True
except ImportError:
    PYPANDOC_EXISTS = False

ROOT = Path(".")
README_PATH = ROOT / "README.md"

if PYPANDOC_EXISTS:
    with README_PATH.open(encoding="utf-8") as f:
        LONG_DESCRIPTION = pypandoc.convert_text(f.read(), "rst", format="md")
else:
    warnings.warn("PyPandoc is not found! Please install it before building wheels.")
    LONG_DESCRIPTION = ""

setup(
    name="enforce",
    version="0.3.5",
    description="Python 3.5+ library for integration testing and data validation through configurable and optional runtime type hint enforcement.",
    long_description=LONG_DESCRIPTION,
    url="https://github.com/RussBaz/enforce",
    author="RussBaz",
    author_email="RussBaz@users.noreply.github.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
    ],
    keywords="""typechecker validation testing runtime type-hints typing decorators""",
    packages=["enforce"],
    install_requires=["wrapt"],
)
