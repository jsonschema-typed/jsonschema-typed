"""Install jsonschema-typed."""

import os
from setuptools import setup

from version import get_version

repo_base_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(repo_base_dir, "README.md")) as f:
    description = f.read()

setup(
    name="jsonschema-typed",
    author="Erick Peirson, Bendik Samseth, Felix von Drigalski",
    author_email="FvDrigalski@gmail.com",
    url="https://github.com/jsonschema-typed/jsonschema-typed",
    python_requires=">=3.7",  # Really should have 3.8 for Final and Literal, but usable without.
    license="MIT",
    version=get_version(),
    packages=["jsonschema_typed"],
    package_data={"jsonschema_typed": ["py.typed"]},
    zip_safe=False,
    install_requires=[
        "jsonschema>=3.2.0",
        "mypy>=0.761",
    ],  # Possibly not so strict, but don't want to check.
    description="Automatic type annotations from JSON schemas",
    long_description=description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Testing",
        "Typing :: Typed",
    ],
)
