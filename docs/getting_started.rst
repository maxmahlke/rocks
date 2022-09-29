
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

Optional but fun: Interactive Search
====================================

``rocks`` provides an interactive search dialogue using the `fzf
<https://github.com/junegunn/fzf/>`_  fuzzy-finder which is triggered if
commands that expect an :term:`asteroid identifier<Identifier>` as argument are
called without argument.\ [#f1]_ In the example below, asteroid (3834) *Zappafrank* is
selected interactively from all 1,218,250 recognised asteroid names:

.. code-block:: bash

    $ rocks who

      (225250)  Georgfranziska
      (16127)   Farzan-Kashani
      (520)     Franziska
      (3183)    Franzkaiser
    > (3834)    Zappafrank

    > frank za  < 5/1218250

The ``fzf`` tool needs to be installed separately from ``rocks``. On most
systems (Linux + MacOS), this requires a single command on the terminal, as
explained in the `fzf documentation
<https://github.com/junegunn/fzf/#installation>`_

.. rubric:: Footnotes
   :caption:

.. [#f1] Useful in cases such as for ``(229762) G!kun||'homdima``: Tpying ``gkun`` is sufficient to find the asteroid in the proposed list.
