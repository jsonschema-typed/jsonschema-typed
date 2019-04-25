"""Install jsonschema-typed."""

from setuptools import setup, find_packages


setup(
    name='jsonschema-typed',
    version='0.1.0',
    packages=['jsonschema_typed'],
    zip_safe=False,
    install_requires=[
        'jsonschema>=3.0.1',
        'mypy>=0.701'
    ]
)
