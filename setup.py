# -*- coding: utf-8 -*-
"""Setup configuration for RadioUnlock."""

from setuptools import setup, find_packages

setup(
    name="radiocodes",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["PySide6>=6.5.0"],
    entry_points={
        "console_scripts": [
            "radiocodes=radiocodes.main:main",
        ],
    },
    python_requires=">=3.8",
)
