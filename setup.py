from setuptools import setup, find_packages

setup(
    name="taxengine",
    version="0.9.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "taxengine=src.main:main",
        ],
    },
)