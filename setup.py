import os

from setuptools import find_packages, setup

import rocks

setup(
    name="rocks",
    version=rocks.__version__,
    python_requires='>=3.6',
    data_files=[os.path.join(os.path.expanduser("~"), ".cache/rocks")],
    packages=find_packages("rocks"),
    include_package_data=True,
    description="For space rocks.",
    py_modules=["rocks"],
    install_requires=[
        "aiohttp",
        "click",
        "iterfzf",
        "matplotlib",
        "numpy",
        "pandas",
        "rich>=8",
        "requests",
    ],
    entry_points="""
        [console_scripts]
        rocks=rocks.cli:cli_rocks
    """,
)
