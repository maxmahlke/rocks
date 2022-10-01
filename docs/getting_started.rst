
.. |br| raw:: html

     <br>

###############
Getting started
###############

Install ``rocks``
=================


``rocks`` is available on the `python package index <https://pypi.org>`_ as *space-rocks*:

.. code-block:: bash

   $ pip install space-rocks

The minimum version requirement for ``python`` is ``3.7``. After
installation, you have the ``rocks`` executable available system-wide.
In addition, you can now import the ``rocks`` ``python`` package.


.. tab-set::

  .. tab-item:: Command Line

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


  .. tab-item :: python


     .. code-block:: python

         >>> import rocks

We are actively developing ``rocks`` and `new versions
<https://github.com/maxmahlke/rocks/blob/master/CHANGELOG.md>`_ come out
frequently. If you encounter a bug, a first step to resolve it is to
:ref:`clear your cache directory <cache_directory>` and to update to the latest
version using

.. code-block:: bash

   $ pip install -U space-rocks


.. _install_fzf:

Optional: Interactive Search
============================

``rocks`` provides an interactive search dialogue using the `fzf
<https://github.com/junegunn/fzf/>`_  fuzzy-finder which is triggered if
commands that expect an :term:`asteroid identifier<Identifier>` as argument are
called without argument.\ [#f1]_

The ``fzf`` tool needs to be installed separately from ``rocks``. On most
systems (Linux + MacOS), this requires a single command on the terminal, as
explained in the `fzf documentation
<https://github.com/junegunn/fzf/#installation>`_

.. raw:: html

    <style> .blue {color:blue;} </style>

.. role:: blue

.. raw:: html

    <style> .coral {color:LightCoral;} </style>

.. role:: coral

.. admonition:: Hint
   :class: tip

   Terms highlighted in :coral:`light red` in the text show the term definition when placing the cursor on top.

.. rubric:: Footnotes
   :caption:

.. [#f1] Useful in cases such as for ``(229762) G!kun||'homdima``: Typing ``gkun`` is sufficient to find the asteroid in the proposed list.
