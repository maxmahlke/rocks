#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 10 May 2020

    Primitive rocks test functions

    Call as:	python rocks_test.py
'''
import numpy as np

from rocks import names
from rocks import properties

if __name__ == '__main__':

    # A collection of asteroid identifiers with various degrees of abstraction
    ssos = [4, 'eos', '1992EA4', 'SCHWARTZ', '1950 RW', '2001je2', '2010 OR']

    # Resolve their names and numbers
    names_numbers = names.get_name_number(ssos, progress=False)

    names = [nn[0] for nn in names_numbers]

    # Get their taxonomy
    taxa = properties.get_property('taxonomy', names, verbose=True,
                                   skip_quaero=True)
    classes = [t[0] for t in taxa]

    print(list(zip(names, classes)))

    # Get albedos
    albedos = properties.get_property('albedo', names, verbose=True,
                                      skip_quaero=True)
    albs = [a[0] for a in albedos]

    print(list(zip(names, albs)))

    if names_numbers != [('Vesta', 4), ('Eos', 221), ('1992 EA4', 30863),
                         ('Schwartz', 13820), ('Gyldenkerne', 5030),
                         ('2001 JE2', 131353), ('2010 OR', np.nan)]:
        print('Error in the names module')

    if classes != ['V', 'K', 'Ds', 'B', False, 'CX', False]:
        print('Error in properties taxonomy module')
