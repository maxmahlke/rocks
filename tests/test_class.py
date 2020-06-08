#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 02 June 2020

    Test class method

    Call as:	pytest test_class.py
'''
import pytest

from rocks.core import Rock

IDs = ['ceres', '1807 FA', 10, 20.]
NANUS = [(1, 'Ceres'), (4, 'Vesta'), (10, 'Hygiea'),
         (20, 'Massalia')]


@pytest.mark.parametrize('id_, nanu', zip(IDs, NANUS), ids=str)
def test_instantiation(id_, nanu):
    '''Verify class instantiation with str, int, float.'''
    SSO = Rock(id_)
    assert (SSO.number, SSO.name) == nanu


Ceres = Rock('Ceres')
print(Ceres.taxonomy)
print(Ceres.taxonomy.shortbib)
print(Ceres.taxonomies)
print(Ceres.taxonomies.shortbib)

print(Ceres.albedo)
print(Ceres.albedos)
print(Ceres.albedos.err_albedo)
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


