#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 02 June 2020

    Core class of rocks package

    Call as:	rocks
'''
from concurrent.futures import ProcessPoolExecutor as Pool
from functools import partial
import keyword
import warnings

import numpy as np
import pandas as pd
from tqdm import tqdm

from rocks import names
from rocks import properties
from rocks import tools


class Rock:
    'For space rocks. Instance for accessing the SsODNet:SSOCard'

    def __init__(self, identifier, only=[]):
        '''Identify an asteroid and retrieve its properties from SsODNet.

        Parameters
        ----------
        identifier : str, int, float
            Identifying asteroid name, designation, or number
        only : list of str
            Optional: only get the specified propertiers.
            By default retrieves all properties.

        Returns
        -------
        rocks.core.Rock
            An asteroid class instance, with its properties as attributes.

        Notes
        -----
        If the asteroid could not be identified, the name and number are None
        and no further attributes are set.

        Example
        -------
        >>> from rocks.core import Rock
        >>> Ceres = Rock('ceres')
        >>> Ceres.taxonomy
        'C'
        '''

        self.name, self.number = names.get_name_number(
            identifier,
            parallel=1,
            progress=False,
            verbose=False
        )

        if not isinstance(self.name, str):
            warnings.warn(f'Could not identify "{identifier}"')
            return
        if not isinstance(only, list):
            raise TypeError(f'Type of "only" is {type(only)}, '
                            f'excpeted list.')
        if not all(isinstance(param, str) for param in only):
            raise ValueError('List of requested properties can only '
                             'contain str.')

        # Set attributes using datacloud
        data_ = tools.get_data(self.name)

        if data_ is False:
            warnings.warn(f'Could not retrieve data for ({self.number}) '
                          f'{self.name}.')
            return

        for prop, setup in properties.PROPERTIES.items():

            if only and prop not in only:
                continue

            data = data_.copy()
            for key in setup['ssodnet_path']:
                data = data[key]

            setattr(
                self,
                setup['collection'],
                listParameter(data, setup['attribute'], type_=setup['type'])
            )

            if setup['type'] is float:
                setattr(
                    self,
                    prop,
                    floatParameter(
                        setup['selection'](data),
                        setup['attribute']
                    ),
                )

            elif setup['type'] is str:
                setattr(
                    self,
                    prop,
                    stringParameter(
                        setup['selection'](data),
                        setup['attribute']
                    ),
                )

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

    def __new__(self, data, prop=False):
        if prop is False:
            return str.__new__(self, data)
        else:
            return str.__new__(self, data[prop])

    def __init__(self, data, prop):
        str.__init__(data[prop])

        for key, value in data.items():

            kw = key if not keyword.iskeyword(key) else key + '_'
            setattr(self, kw, value)


class floatParameter(float):
    '''For asteroid parameters which are floats, e.g. albedo.'''

    def __new__(self, data, prop=False):
        if prop is False:
            return float.__new__(self, data)
        else:
            return float.__new__(self, data[prop])

    def __init__(self, data, prop):
        float.__init__(data[prop])

        for key, value in data.items():

            kw = key if not keyword.iskeyword(key) else key + '_'
            setattr(self, kw, value)


class listParameter(list):
    '''For several measurements of a single parameters of any type.'''

    def __init__(self, data, prop, type_):
        list.__init__(self, [type_(d[prop]) for d in data])

        self.datatype = type_

        for key in data[0].keys():

            # Catches python-keywords
            kw = key if not keyword.iskeyword(key) else key + '_'

            # "err_property" -> err
            if kw == f'err_{prop}':
                kw = 'error'

            # Proper typing of values
            values = [d[key] for d in data]

            try:
                values = [float(v) for v in values]
            except ValueError:
                pass

            setattr(self, kw, values)

    def weighted_average(self):
        '''Compute weighted average of float-type parameters.

        Returns
        -------
        (float, float)
            Weighted average and its uncertainty.
        '''
        if self.datatype is not float:
            raise TypeError('Property is not of type float.')

        observable = np.array(self)

        # Make uniform weights in case no errors are provided
        if not hasattr(self, 'error'):
            error = np.ones(len(self))
            weights = np.ones(len(self))
        else:
            # Remove measurements where the error is zero
            error = np.array(self.error)
            observable = observable[error != 0]
            error = error[error != 0]

        # Compute normalized weights
        weights = 1 / np.array(error)**2
        weights = weights / sum(weights)

        # Compute weighted average and uncertainty
        avg = np.average(observable, weights=weights)

        # Bevington's implementation
        std_avg = np.sqrt(
            1 / (len(self) - 1) * sum(w * (s - avg)**2 for w, s in
                                      zip(weights, self))
        )

        print('Values: ', observable)
        print('Errors:', error)

        print('Bevingtons std mean:', std_avg)
        # Wikipedia
        std_avg = np.sqrt(
            sum(w**2 * e**2 for w, e in zip(weights, error))
        )
        print('Wikipedias std mean:', std_avg)
        return (avg, std_avg)

    def scatter(self):
        '''Placeholder'''

        # "self" is a list of either floats or strings
        print(self)
        # On top, self has attributes.
        print(self.shortbib)


def many_rocks(ids, properties, parallel=4, progress=True, verbose=False):
    '''Get Rock instances with a subset of properties for many asteroids.

    Queries SsODNet datacloud. Can be passed a list of identifiers.
    Optionally performs a quaero query to verify the asteroid identitfy.

    Parameters
    ----------
    ids : list of str, list of int, list of float, np.array, pd.Series
        An iterable containing asteroid identifiers.
    properties : list of str
        Asteroid properties to get.
    parallel : int
        Number of jobs to use for queries. Default is 4.
    progress : bool
        Show progress. Default is True.
    verbose : bool
        Print request diagnostics. Default is False.

    Returns
    -------
    list of Rock
        A list of Rock instances containing the requested properties as
        attributes.
    '''
    if isinstance(ids, pd.Series):
        ids = ids.values

    build_rock = partial(Rock, only=properties)

    # Create Rocks
    pool = Pool(max_workers=parallel)
    rocks = list(tqdm(pool.map(build_rock, ids), total=len(ids),
                      disable=not progress))
    return rocks
