#########
``rocks``
#########

*for space-rocks*.

A ``python`` client to retrieve and explore asteroid data from
`SsODNet <https://ssp.imcce.fr/webservices/ssodnet/>`_.
Latest version: 1.4.10  - `What's new? <https://github.com/maxmahlke/rocks/blob/master/CHANGELOG.md>`_

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
   +-----------+---------+--------+-----------+------------------+------+--------+
   | scheme    | complex | method | waverange | shortbib         | year | class_ |
   +-----------+---------+--------+-----------+------------------+------+--------+
   | Tholen    | S       | Phot   | VIS       | Tholen+1989      | 1989 | S      |
   | Bus       | K       | Spec   | VIS       | Bus&Binzel+2002  | 2002 | K      |
   | Bus       | K       | Spec   | VIS       | MotheDiniz+2005  | 2005 | K      |
   | Bus       | K       | Spec   | VISNIR    | MotheDiniz+2008a | 2008 | K      |
   | Bus-DeMeo | K       | Spec   | VISNIR    | Clark+2009       | 2009 | K      |
   | Bus-DeMeo | K       | Spec   | VISNIR    | DeMeo+2009       | 2009 | K      |
   +-----------+---------+--------+-----------+------------------+------+--------+

   $ rocks masses Eos
    +----------+----------+---------+-------------+------+
    | mass     | err_mass | method  | shortbib    | year |
    +----------+----------+---------+-------------+------+
    | 2.39e+18 | 5.97e+17 | DEFLECT | Goffin+2014 | 2014 |
    +----------+----------+---------+-------------+------+



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
