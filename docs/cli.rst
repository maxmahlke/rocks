.. _cli:

######################
Command Line Interface
######################

The ``rocks`` executable is useful for quick exploration of asteroid data from the command line / terminal.
The most general use case is to provide an asteroid property and an asteroid identifier to echo the value from the ``ssoCard``.

.. code-block:: bash

   $ rocks diameter Pallas
   514.102 +- 3.475 km

Furthermore, there are :ref:`commands<commands>` to identify asteroids, interact with the cached ``ssoCards``, look up available properties, and more.

.. code-block:: bash

   $ rocks identify 9885
   (9885) Linux

Data exploration
================

The general structure is ``rocks [property] [id]``. ``property`` refers to the property name in the ssoCard structure, ``id`` refers to the asteroid name, designation, or number. Aliases such as packed designations are also recognized.


.. code-block:: bash       
                           
   $ rocks class_ ceres    
   Dwarf Planet

   $ rocks proper_semi_major_axis ceres
   2.767 +- 4.71e-06

If the key ambiguous, the higher level attribute is preferred.

.. code-block:: bash       
                           
  $ rocks class_ 4
  MB>Inner

  $ rocks taxonomy.class_ 4
  V

The names of the accepted properties are echoed with :ref:`rocks properties<rocks-props>`.

Collections of properties from datacloud can also be printed. Giving only the name of the catalogue prints a general overview.

.. code-block:: bash       
                           
  $ rocks masses Fortuna
  ┌───────────┬───────────┬─────────┬─────────────────────┬──────┐
  │ mass      │ err_mass  │ method  │ shortbib            │ year │
  ├───────────┼───────────┼─────────┼─────────────────────┼──────┤
  │ 1.99e+19  │ 1.39e+19  │ DEFLECT │ Ivantsov+2007       │ 2007 │
  │ 1.08e+19  │ 1.51e+18  │ DEFLECT │ Baer+2008           │ 2008 │
  │ 4.02e+18  │ 3.98e+17  │ EPHEM   │ Fienga+2009         │ 2009 │
  │ 6.94e+18  │ 6.94e+17  │ EPHEM   │ Folkner+2009        │ 2009 │
  │ 6.37e+18  │ 2.9e+18   │ DEFLECT │ Somenzi+2010        │ 2010 │
  │ 8.31e+18  │ 7.16e+17  │ DEFLECT │ Baer+2011           │ 2011 │
  │ 6.37e+18  │ 1.05e+18  │ EPHEM   │ Konopliv+2011       │ 2011 │
  │ 1e+19     │ 1.08e+18  │ DEFLECT │ Zielenbach+2011     │ 2011 │
  │ 1.02e+19  │ 9.47e+17  │ DEFLECT │ Zielenbach+2011     │ 2011 │
  │ 1.01e+19  │ 9.35e+17  │ DEFLECT │ Zielenbach+2011     │ 2011 │
  │ 1.05e+19  │ 1.23e+18  │ DEFLECT │ Zielenbach+2011     │ 2011 │
  │ 8.35e+18  │ 5.97e+17  │ EPHEM   │ Fienga+2011         │ 2011 │
  │ 9.73e+18  │ 1.01e+18  │ EPHEM   │ Fienga+2013         │ 2013 │
  │ 7.79e+18  │ 8.99e+17  │ EPHEM   │ Kuchynka+2013       │ 2013 │
  │ 8.67e+18  │ 2.59e+17  │ EPHEM   │ Pitjeva+2013        │ 2013 │
  │ 8e+18     │ 9.35e+17  │ EPHEM   │ Fienga+2014         │ 2014 │
  │ 8.95e+18  │ 1.99e+17  │ DEFLECT │ Goffin+2014         │ 2014 │
  │ 8.83e+18  │ 4.18e+17  │ DEFLECT │ Kochetova+2014      │ 2014 │
  │ 1.03e+19  │ 5.61e+17  │ EPHEM   │ Viswanathan+2017    │ 2017 │
  │ 2.8e+18   │ 3.11e+18  │ DEFLECT │ Siltala+2017        │ 2017 │
  │ 2.21e+19  │ 1.01e+19  │ DEFLECT │ Siltala+2017        │ 2017 │
  │ 1.102e+19 │ 6.324e+17 │ EPHEM   │ Baer+2017           │ 2017 │
  │ 7.78e+18  │ 7.93e+18  │ DEFLECT │ Siltala&Granvik2019 │ 2020 │
  │ 7.84e+18  │ 7.24e+17  │ EPHEM   │ Fienga+2020         │ 2020 │
  └───────────┴───────────┴─────────┴─────────────────────┴──────┘

Providing the catalogue name and a property returns the property.

.. code-block:: bash       

  $ rocks diamalbedo.albedo 551
  [0.043, 0.057, 0.036, 0.044, 0.04, 0.05, 0.06, 0.05, 0.038, 0.04, 0.058, 0.045]


The ``diamalbedo`` catalogue is aliased to ``diameters`` and ``albedos``.

.. _commands:

More commands
=============


rocks clear
-----------

Remove all ssoCards from the cache directory.

rocks docs
----------

Open this documentation in browser tab.

rocks id
--------

Identify an asteroid using its number, name, or designation. Aliases and packed designations from the Minor Planet Centre are recognised as well.
``rocks`` uses SsODNet:quaero to resolve the identities.


.. code-block:: bash       
                           
   $ rocks id 221
   (221) Eos               

   $ rocks id Schwartz
   (13820) Schwartz

   $ rocks id "1902 UG"
   (19) Fortuna

   $ rocks id J65B00A
   (1727) Mette

The command is aliased to ``rocks id`` as well.

rocks info
----------

Echo the ssoCard of an asteroid in JSON format.

.. _rocks-props:

rocks parameters
----------------

Echo the structure of the ssoCard. Can be used in combination with ``grep`` to find the right property name to provide to ``rocks``

.. code-block:: bash

 $ rocks properties | grep semi_major
 'parameters.dynamical.osculating_elements.semi_major_axis',
 'parameters.dynamical.proper_elements.proper_semi_major_axis',
 'parameters.dynamical.uncertainty.osculating_elements.semi_major_axis',
 'parameters.dynamical.uncertainty.proper_elements.proper_semi_major_axis',

rocks status
------------

Echo the number of cached ssoCards and checks if any are outdated. Offers to update outdated cards.
Offers to update the asteroid name-number index. Further, retrieves the current ssoCard structure template from SsODNet.
