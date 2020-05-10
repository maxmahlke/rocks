from setuptools import find_packages, setup

setup(
    name='rocks',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    py_modules=['rocks'],
    install_requires=[
        'click',
        'iterfzf',
        'numpy',
        'pandarallel',
        'pandas',
        'tqdm'
    ],
    entry_points='''
        [console_scripts]
        rocks=rocks.cli:cli_rocks
    ''',
)
