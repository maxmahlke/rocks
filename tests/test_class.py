#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 02 June 2020

    Test class method

    Call as:	pytest test_class.py
'''

from rocks.core import Rock


Ceres = Rock('Ceres')
Pallas = Rock('pallas')
Juno = Rock(3.)

_2010OR = Rock('2010OR')
_2010OR2 = Rock('2010OR')

print(_2010OR == _2010OR2)
# equality comparison happens on name only
a = {Ceres: 'this'}

print(sorted([Juno, Pallas, Ceres, _2010OR]))
# print(Juno.number)
# Juno.number = 2
# print(Juno.number)
