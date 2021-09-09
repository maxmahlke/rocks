Getting started
===============

Install from PyPI
-----------------

``rocks`` is available on the `python package index <https://pypi.org>`_ as *space-rocks*:

.. code-block:: bash

   $ pip install space-rocks

Cache directory
---------------

``rocks`` retrieves all requested asteroid data from SsODNet. Since you typically need this data
again soon (e.g. when re-executing the analysis script), the data is stored in a cache directory located at ``~/.cache/rocks``, where the ``~`` character refers to the user's home directory.
This directory is created if it does not exist when ``rocks`` is used.

After some weeks / months, the data in the cached ssoCards may be outdated. You can update all outdated cards using

.. code-block:: bash

   $ rocks status

You can delete all cached ssoCards by running

.. code-block:: bash

   $ rocks clear

Asteroid Name-Number index
--------------------------

The first step in almost any ``rocks`` function is to identify an asteroid based on the passed
designation or number. To reduce the cost of this query as much as possible, ``rocks`` keeps a local
index of asteroid name and number combinations in the cache directory, called ``index.pkl``. If the index is not available as ``rocks`` is invoqued, it will offer to retrieve it from the `GitHub repository <https://github.com/maxmahlke/rocks`_.
