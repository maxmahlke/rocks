###############
Getting started
###############

Install from PyPI
=================


``rocks`` is available on the `python package index <https://pypi.org>`_ as *space-rocks*:

.. code-block:: bash

   $ pip install space-rocks

Note that the minimum version requirement for `python` is `3.7`. After
installation, you should have the ``rocks`` executable available system-wide.

.. code-block:: bash

   $ rocks

   Usage: rocks [OPTIONS] COMMAND [ARGS]...

   CLI for minor body exploration.

   Options:
     --version  Show the version and exit.
     --help     Show this message and exit.

   Commands:
     docs        Open the rocks documentation in browser.
     id          Resolve the asteroid name and number from string input.
     info        Print the ssoCard of an asteroid.
     parameters  Print the ssoCard structure and its description.
     status      Echo the status of the ssoCards and datacloud catalogues.

In addition, you can now import the ``rocks`` ``python`` package.

.. code-block:: python

   >>> import rocks


.. _cache-directory:

Cache Directory
===============

``rocks`` retrieves all requested asteroid data from :term:`SsODNet`. Since you
typically need this data again soon (e.g. when re-executing the analysis
script), it is stored in a :term:`cache directory<Cache Directory>` located at
``~/.cache/rocks``, where the ``~`` character refers to the user's home
directory. This directory is created if it does not exist when ``rocks`` is
invoked.

Asteroid Name-Number Index
==========================

The first step in almost any ``rocks`` function is to identify an asteroid
based on an :term:`identifier<Identifier>`. To reduce the time of this
resolution as much as possible, ``rocks`` keeps a local index of asteroid names
and numbers in a file called ``index.pkl`` in the cache directory. This index
is retrieved from :term:`SsODNet` if it does not exist when ``rocks`` is
invoked.
