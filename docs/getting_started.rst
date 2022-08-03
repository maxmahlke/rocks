
.. |br| raw:: html

     <br>

###############
Getting started
###############

Install from PyPI
=================


``rocks`` is available on the `python package index <https://pypi.org>`_ as *space-rocks*:

.. code-block:: bash

   $ pip install space-rocks

The minimum version requirement for `python` is `3.7`. After
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
     who         Get name citation of asteroid from MPC.


In addition, you can now import the ``rocks`` ``python`` package.

.. code-block:: python

   >>> import rocks


.. _cache-directory:

Cache Directory
===============

``rocks`` retrieves all requested asteroid data from :term:`SsODNet`. Since you
typically need this data again soon (e.g. when re-executing the analysis
script), it is stored in a :term:`cache directory<Cache Directory>` located at
``~/.cache/rocks``, where the ``~`` character refers to the home
directory. This directory is created if it does not exist when ``rocks`` is
invoked.

|br|

The first step in almost any ``rocks`` function is to identify an asteroid
based on an :term:`identifier<Identifier>`. To reduce the time of this
resolution as much as possible, ``rocks`` keeps a local index of asteroid names
and numbers split over several files in the cache directory. This index
is retrieved from :term:`SsODNet` if it does not exist when ``rocks`` is
invoked.

The data in the cache directory can be updated or removed using the ``$ rocks status`` command:

.. code-block:: bash

   $ rocks status

   Contents of /home/mmahlke/.cache/rocks:

           41 ssoCards
           15 datacloud catalogues

           Asteroid name-number index updated on 12 Jul 2022

   Update or clear the cached ssoCards and datacloud catalogues?
   [0] Do nothing [1] Clear the cache [2] Update the data (1): 1

   Clearing the cached ssoCards and datacloud catalogues..

   Update the asteroid name-number index?
   [0] No [1] Yes (1): 1

   Building index ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

Optional: Interactive Finder
============================


Sometimes you have the name of an asteroid in your head but you don't quite
recall its spelling. In this case, ``rocks`` provides an interactive search dialogue
using the `fzf <https://github.com/junegunn/fzf/>`_  fuzzy-finder.
In the example below, the citation of asteroid (3834) *Zappafrank* is retrieved
from the Minor Planet Centre. Instead of entering the asteroid name when typing
the command, it is selected interactively from all 1,218,250 recognised
asteroid names:

.. code-block:: bash

    $ rocks who

      (225250)  Georgfranziska
      (16127)   Farzan-Kashani
      (520)     Franziska
      (3183)    Franzkaiser
    > (3834)    Zappafrank

    > frank za  < 5/1218250

The ``fzf`` tool needs to be installed separately from ``rocks``. On most systems (Linux + MacOS),
this requires a single command on the terminal, as explained in the `fzf documentation <https://github.com/junegunn/fzf/#installation>`_
