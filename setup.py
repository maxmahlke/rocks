import os

from setuptools import find_packages, setup

# ReadTheDocs install does not allow data_files
if os.environ.get("READTHEDOCS", False):
    include_package_data = False
    data_files = []
else:
    include_package_data = True
    data_files = [os.path.join(os.path.expanduser("~"), ".cache/rocks")]

setup(
    name="rocks",
    version="0.1.0",
    python_requires=">=3.4",
    packages=find_packages("rocks"),
    include_package_data=include_package_data,
    data_files=data_files,
    description="For space rocks.",
    py_modules=["rocks"],
    install_requires=[
        "aiohttp[speedups]",
        "aiodns",
        "chardet<4.0",
        "cchardet",
        "click",
        "iterfzf",
        "matplotlib",
        "numpy",
        "pandas",
        "rich>=8",
        "requests",
        "tqdm",
    ],
    extras_require={
        "docs": ["sphinx_redactor_theme"],
    },
    entry_points="""
        [console_scripts]
        rocks=rocks.cli:cli_rocks
    """,
)
