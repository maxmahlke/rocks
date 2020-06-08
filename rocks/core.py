#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 02 June 2020

    Core class of rocks package

    Call as:	rocks
'''
import keyword
import warnings

import numpy as np

from rocks import names
from rocks import taxonomy
from rocks import tools


class Rock:
    'For space rocks. Instance for accessing the SsODNet:SSOCard'

    def __init__(self, identifier):

        # Identify the object
        self.name, self.number = names.get_name_number(identifier,
                                                       parallel=1,
                                                       progress=False,
                                                       verbose=False
                                                       )
        if not isinstance(self.name, str):
            warnings.warn(f'Could not identify "{identifier}"')
            return

        # Set attributes using datacloud
        data = tools.get_data(self.name)

        # albedo
        self.albedos = listParameter(data['diamalbedo'], 'albedo', type_=float)
        self.albedo = np.mean(self.albedos)

        # taxonomy
        self.taxonomies = listParameter(data['taxonomy'], 'class', type_=str)
        selected_taxonomy = taxonomy.select_taxonomy(data['taxonomy'],
                                                     from_Rock=True)
        self.taxonomy = stringParameter(selected_taxonomy, 'class')

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.__class__.__qualname__ +\
            f'(number={self.number!r}, name={self.name!r})'

    def __str__(self):
        return f'({self.number}) {self.name}'

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.name == other.name
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return (self.number, self.name) < (other.number, other.name)
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return (self.number, self.name) <= (other.number, other.name)
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return (self.number, self.name) > (other.number, other.name)
        return NotImplemented

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return (self.number, self.name) >= (other.number, other.name)
        return NotImplemented


class stringParameter(str):
    '''For asteroid parameters which are strings, e.g. taxonomy.'''

    def __new__(self, data, key):
        return str.__new__(self, data[key])

    def __init__(self, data, key):
        str.__init__(data[key])

        for key, value in data.items():
            if keyword.iskeyword(key):
                key = key + '_'
            setattr(self, key, value)


class floatParameter(float):
    '''For asteroid parameters which are floats, e.g. albedo.'''

    def __new__(self, data, key):
        return float.__new__(self, data[key])

    def __init__(self, data, key):
        float.__init__(data[key])

        for key, value in data.items():
            if keyword.iskeyword(key):
                key = key + '_'
            setattr(self, key, value)


class listParameter(list):
    '''For several measurements of a single parameters of any type.'''

    def __init__(self, data, key, type_):
        list.__init__(self, [type_(d[key]) for d in data])

        for key in data[0].keys():
            kw = key if not keyword.iskeyword(key) else key + '_'
            setattr(self, kw, [d[key] for d in data])
