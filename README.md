<p align="center">
  <img width="260" src="https://raw.githubusercontent.com/maxmahlke/rocks/master/docs/_static/logo_rocks.svg">
</p>

<p align="center">
  <a href="https://github.com/maxmahlke/rocks#features"> Features </a> - <a href="https://github.com/maxmahlke/rocks#install"> Install </a> - <a href="https://github.com/maxmahlke/rocks#documentation"> Documentation </a>
</p>

<div align="center">
  <a href="https://img.shields.io/pypi/pyversions/space-rocks">
    <img src="https://img.shields.io/pypi/pyversions/space-rocks"/>
  </a>
  <a href="https://img.shields.io/pypi/v/space-rocks">
    <img src="https://img.shields.io/pypi/v/space-rocks"/>
  </a>
  <a href="https://readthedocs.org/projects/rocks/badge/?version=latest">
    <img src="https://readthedocs.org/projects/rocks/badge/?version=latest"/>
  </a>
  <a href="https://arxiv.org/abs/2209.10697">
    <img src="https://img.shields.io/badge/arXiv-2209.10697-f9f107.svg"/>
  </a>
</div>


## Features

Explore asteroid data on the command-line...

``` sh
$ rocks id 221
(221) Eos

$ rocks class Eos
MB>Outer

$ rocks albedo Eos
0.136 +- 0.004

$ rocks taxonomy Eos
K

$ rocks density Eos
4.559e+03 +- 1.139e+03 kg/m$^3$
```

... and in a `python` script.

``` python
>>> import rocks
>>> rocks.identify("1902ug")
('Fortuna', 19)
>>> ceres = rocks.Rock("ceres")
>>> ceres.diameter.value
848.4
>>> ceres.diameter.unit
'km'
>>> ceres.mass.value
9.384e+20
>>> ceres.mass.error
6.711e+17
```

## Install

Install from PyPi using `pip`:

     $ pip install space-rocks

The minimum required `python` version is 3.7.


## Documentation

Check out the documentation at [rocks.readthedocs.io](https://rocks.readthedocs.io/en/latest/) or run

     $ rocks docs

For a quick overview, check out the jupyter notebooks:

[Basic Usage](https://github.com/maxmahlke/rocks/blob/master/docs/tutorials/rocks_basic_usage.ipynb) - [Bibliography Management](https://github.com/maxmahlke/rocks/blob/master/docs/tutorials/literature.ipynb)
