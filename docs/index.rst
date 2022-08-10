#########
``rocks``
#########

.. raw:: html

    <style> .gray {color:#979eab} </style>

.. role:: gray

:gray:`Latest version: 1.5.11  -` `What's new? <https://github.com/maxmahlke/rocks/blob/master/CHANGELOG.md>`_ :gray:`| Bug or feature request? Open an issue on` `GitHub <https://github.com/maxmahlke/rocks/issues>`_:gray:`.`

A ``python`` client to retrieve and explore asteroid data from
`SsODNet <https://ssp.imcce.fr/webservices/ssodnet/>`_.


.. highlight:: python



via the Command Line
====================

Quick exploration of asteroid parameters using the ``rocks`` :ref:`command-line interface<cli>`.

.. code-block:: bash

   $ rocks id 221
   (221) Eos

   $ rocks class Eos
   MB>Outer

   $ rocks albedo Eos
   0.136 +- 0.004

   $ rocks taxonomy Eos
   K

   $ rocks taxonomies Eos
   +---+--------+---------+--------+-----------+-----------+------------------+
   |   | class_ | complex | method | waverange | scheme    | shortbib         |
   +---+--------+---------+--------+-----------+-----------+------------------+
   | 1 | S      | S       | Phot   | VIS       | Tholen    | Tholen+1989      |
   | 2 | K      | K       | Spec   | VIS       | Bus       | Bus&Binzel+2002  |
   | 3 | K      | K       | Spec   | VIS       | Bus       | MotheDiniz+2005  |
   | 4 | K      | K       | Spec   | VISNIR    | Bus       | MotheDiniz+2008a |
   | 5 | K      | K       | Spec   | VISNIR    | Bus-DeMeo | Clark+2009       |
   | 6 | K      | K       | Spec   | VISNIR    | Bus-DeMeo | DeMeo+2009       |
   | 7 | K      | K       | Spec   | VISNIR    | Mahlke    | Mahlke+2022      |
   +---+--------+---------+--------+-----------+-----------+------------------+

   $ rocks masses Eos
   +---+-------------+-------------+---------------+---------+--------------+
   |   | mass        | err_mass_up | err_mass_down | method  | shortbib     |
   +---+-------------+-------------+---------------+---------+--------------+
   | 1 | 1.22125e+18 | 0.0         | 0.0           | EPHEM   | Folkner+2014 |
   | 2 | 2.39e+18    | 5.97e+17    | -5.97e+17     | DEFLECT | Goffin+2014  |
   | 3 | 1.04688e+18 | 5.16159e+17 | -5.16159e+17  | EPHEM   | Fienga+2019  |
   +---+-------------+-------------+---------------+---------+--------------+


via a ``python`` script
=======================

Easy access of asteroid properties using the :ref:`Rock<rock_class>` class.

.. code-block:: python

  >>> from rocks import Rock
  >>> ceres = Rock("ceres")
  >>> ceres.diameter.value
  848.4
  >>> ceres.mass.value
  9.384e+20
  >>> ceres.mass.error
  6.711e+17

See more use cases in the :ref:`Tutorials<Tutorials>`.

**Disclaimer: The SsODNet service and its database are in an alpha version and
under constant revision.
The provided values and access methods may change
without notice.**

.. toctree::
   :maxdepth: 2
   :caption: Contents
   :hidden:

   Getting Started<getting_started>
   Available Data<ssodnet>
   Command Line Interface<cli>
   python Interface<core>
   tutorials
   appendix
   glossary
