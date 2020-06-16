Tools
=====

These are general, low-level utility functions.

.. currentmodule:: tools

Asteroid name-number Index
""""""""""""""""""""""""""
To speed up name-number lookups, a local index file is kept. It contains the
list of numbered asteroids and their names or designations.

.. autofunction:: create_index

.. autofunction:: read_index

The index can be fuzzy-searched interactively using

.. autofunction:: select_sso_from_index

SsODNet Query Functions
"""""""""""""""""""""""

.. autofunction:: get_data

`get_data` calls `query_ssodnet`.

.. autofunction:: query_ssodnet


.. autofunction:: echo_response


.. autofunction:: select_sso_from_index

