"""Install jsonschema-typed."""

from setuptools import setup
import os

repo_base_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(repo_base_dir, "README.md")) as f:
    description = f.read()

setup(
    name="jsonschema-typed-v2",
    author="Bendik Samseth",
    author_email="b.samseth@gmail.com",
    url="https://github.com/bsamseth/jsonschema-typed",
    python_requires=">=3.8",  # At least to develop, possibly importable in lower versions?
    license="MIT",
    version="0.2.0",
    packages=["jsonschema_typed"],
    zip_safe=False,
    install_requires=[
        "jsonschema>=3.2.0",
        "mypy>=0.761",
    ],  # Possibly not so strict, but don't want to check.
    long_description=(
        """This is a fork of Erick Peirson's original `jsonschema_typed`.\n\n"""
        + description
    ),
    long_description_content_type="text/markdown",
)
