#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 02 June 2020

    Test Rock and other classes

    Call as:	pytest test_class.py
'''
from os import path

import json
import pytest

from rocks.core import Rock
from rocks import tools

# IDs = ['ceres', '1807 FA', 10, 20.]
# NANUS = [(1, 'Ceres'), (4, 'Vesta'), (10, 'Hygiea'),
         # (20, 'Massalia')]
IDs = ['ceres', 2, 4.]
NANUS = [(1, 'Ceres'), (2, 'Pallas'), (4, 'Vesta')]
TAX = ['C', 'B', 'V']


@pytest.mark.parametrize('id_, nanu, tax', zip(IDs, NANUS, TAX), ids=str)
def test_instantiation(id_, nanu, tax, monkeypatch):
    '''Verify class instantiation with str, int, float.'''

    monkeypatch.setattr(tools, 'get_data', read_data)

    SSO = Rock(id_)
    assert (SSO.number, SSO.name) == nanu
    assert SSO.taxonomy == tax


@pytest.mark.parametrize('id_, nanu, tax', zip(IDs, NANUS, TAX), ids=str)
def test_partial_instantiation(id_, nanu, tax, monkeypatch):
    '''Verify partial class instantiation with "only"-keyword.'''

    monkeypatch.setattr(tools, 'get_data', read_data)

    SSO = Rock(id_, ['taxonomy'])
    assert (SSO.number, SSO.name) == nanu
    assert SSO.taxonomy == tax
    assert not hasattr(SSO, 'albedo')


# Ceres = Rock('Ceres')
# print(Ceres.taxonomy)
# print(Ceres.taxonomy.shortbib)
# print(Ceres.taxonomies)
# print(Ceres.taxonomies.shortbib)

# print(Ceres.albedo)
# print(Ceres.albedos)
# print(Ceres.albedos.err_albedo)
# C
# ['C', 'G', 'C', 'C']
# Ceres = Rock('Ceres')
# Pallas = Rock('pallas')
# Juno = Rock(3.)

# _2010OR = Rock('2010OR')
# _2010OR2 = Rock('2010OR')

# print(_2010OR == _2010OR2)
# # equality comparison happens on name only
# a = {Ceres: 'this'}

# print(sorted([Juno, Pallas, Ceres, _2010OR]))
# # print(Juno.number)
# # Juno.number = 2
# # print(Juno.number)


# MONKEYPATCH
# Read from file rather than query ssodnet for test
def read_data(name):
    path_data = path.join(path.dirname(__file__),
                          f'data/{name}_datacloud.json')

    with open(path_data, 'r') as file_:
        data = json.load(file_)

    return data['data'][name]
