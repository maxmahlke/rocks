.. _cli:

##########################
The Command Line Interface
##########################

The ``rocks`` command-line executable is useful for quick exploration of
asteroid data from the command line. The most general use case is to provide an
asteroid parameter and :term:`identifier<Identifier>` to echo the value from
the :term:`ssoCard`.

.. code-block:: bash

   $ rocks diameter pallas
   514.1 +- 3.906 km

Furthermore, there are commands to identify asteroids, interact with the cached
:term:`ssoCards<ssoCard>` and :term:`datacloud catalogues<Datacloud
Catalogue>`, look up available asteroid parameters, and more. You can get the list of available
commands by running ``$ rocks``.

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

Data Exploration
================

Getting values from the ssoCard
-------------------------------

To get the value of the ``[parameter]`` (e.g. albedo, diameter) for the
asteroid ``[identifier]`` (e.g. any valid :term:`identifier<Identifier>`) from
the :term:`ssoCard`, use the command of the form ``$ rocks [parameter] [id]``.

.. code-block:: bash

   $ rocks class_ ceres
   Dwarf Planet

   $ rocks proper_semi_major_axis ceres
   2.767 +- 4.71e-06

.. _rocks-props:

The list of accepted parameters names and a brief description is echoed with
the ``$ rocks parameters`` command. This can be used in
combination with ``grep`` to quickly find the right parameter name to provide to
``rocks``.

.. code-block:: bash

 $ rocks parameters | grep period
   'orbital_period': {
       'value': 'Orbital period',
           'min': 'Lower value of uncertainty of the orbital period',
           'max': 'Upper value of uncertainty of the orbital period'
       'period': {
           'value': 'Synodic or sidereal period of rotation',
               'min': 'Lower uncertainty of the period of rotation',
               'max': 'Upper uncertainty of the period of rotation'

The parameter units are echoed using the ``--units/-u`` flag.

.. code-block:: bash

 $ rocks parameters --units | grep period
   'orbital_period': {'value': 'd', 'error': {'min': 'd', 'max': 'd'}}
       'period': {'value': 'h', 'error': {'min': 'h', 'max': 'h'}},

Some parameters have aliases implemented to avoid verbosity. See the
:ref:`list of parameter aliases<Parameter Aliases>` in the appendix.

.. code-block:: bash

   $ rocks proper_semi_major_axis ceres
   2.767 +- 4.71e-06

   $ rocks ap ceres  # same as above, proper semi-major axis
   2.767 +- 4.71e-06

To echo the complete :term:`ssoCard` of an asteroid, use the ``$ rocks info [identifier]`` command.

.. code-block:: bash

   $ rocks info themis
   {
       'id': 'Themis',
       'name': 'Themis',
       'number': 24,
       'type': 'Asteroid',
       'class': 'MB>Outer',
       'parent': 'Sun',
       'system': 'Sun',
       'ssocard': {'version': '0.9.7-rc1', 'datetime': '2021-12-03T09:40:51+00:00'},
       'link': {
           'self': 'http://ssp.imcce.fr/webservices/ssodnet/api/ssocard.php?q=Themis',
           'quaero': 'https://api.ssodnet.imcce.fr/quaero/1/sso/Themis',
           'description': 'http://ssp.imcce.fr/webservices/ssodnet/api/ssocard/description_aster-astorb.json',
           'unit': 'http://ssp.imcce.fr/webservices/ssodnet/api/ssocard/unit_aster-astorb.json'
       },
       'parameters': {
           'dynamical': {
               'orbital_elements': {

    [...]

Getting values from datacloud catalogues
----------------------------------------

In general, if you provide the singular name of a parameter, the value from the
:term:`ssoCard` is returned, while the plural name lists all parameter values
present in the :term:`datacloud catalogues<Datacloud Catalogue>`. You can find
the full :ref:`list of catalogues and their names <Datacloud Catalogue
Attribute Names>` in ``rocks`` in the appendix.

.. code-block:: bash

  $ rocks mass 42
  1.386e+18 +- 1.216e+17 kg

  $ rocks masses 42
  +----------+--------------+--------------+--------+------------------+
  | mass     | err_mass_max | err_mass_min | method | shortbib         |
  +----------+--------------+--------------+--------+------------------+
  | 1.38e+18 | 1.38e+17     | -1.38e+17    | EPHEM  | Folkner+2009     |
  | 1.85e+18 | 5.93e+17     | -5.93e+17    | EPHEM  | Fienga+2011      |
  | 1.5e+18  | 4.5e+17      | -4.5e+17     | EPHEM  | Kuchynka+2013    |
  | 2.15e+17 | 6.69e+17     | -6.69e+17    | EPHEM  | Fienga+2014      |
  | 1.59e+18 | 4.45e+17     | -4.45e+17    | EPHEM  | Viswanathan+2017 |
  +----------+--------------+--------------+--------+------------------+

Specific entries from each :term:`datacloud catalogue<Datacloud Catalogue>` can be accessed by
specifying the parameter name via the dot notation.

.. code-block:: bash

    $ rocks taxonomies 42
    +--------+----------+--------+-----------+-----------+-----------------+
    | class_ | complex_ | method | waverange | scheme    | shortbib        |
    +--------+----------+--------+-----------+-----------+-----------------+
    | S      | S        | Phot   | VIS       | Tholen    | Tholen+1989     |
    | L      | L        | Spec   | VIS       | Bus       | Bus&Binzel+2002 |
    | K      | K        | Spec   | VISNIR    | Bus-DeMeo | DeMeo+2009      |
    | K      | K        | Spec   | NIR       | Bus-DeMeo | Gietzen+2012    |
    +--------+----------+--------+-----------+-----------+-----------------+

    $ rocks taxonomies.scheme 42
    0    Bus-DeMeo
    1    Bus-DeMeo
    2          Bus
    3       Tholen
    Name: scheme, dtype: object


Name Resolution
===============

The ``$ rocks id [identifier]`` command allows for quick name resolution via the command line.
You can pass any valid asteroid :term:`identifier<Identifier>`.

.. code-block:: bash

   $ rocks id 221
   (221) Eos

   $ rocks id Schwartz
   (13820) Schwartz

   $ rocks id "1902 UG"
   (19) Fortuna

   $ rocks id 2012fg3
   (nan) 2012 FG3

   $ rocks id J65B00A
   (1727) Mette

If you have trouble remembering the name of an asteroid, ``rocks`` can give you a hint.

.. code-block:: bash

   $ rocks id barkajdetolli
   rocks: Could not find match for id Barkajdetolli.

   Could this be the rock you're looking for?
     (4524) Barklajdetolli

.. _commands:

More commands
=============

rocks docs
----------

Open this documentation in a new browser tab.

.. _cli_id:


rocks status
------------

Echo the number of cached :term:`ssoCards<ssoCard>` and checks if any are
outdated. Offers to update outdated cards. Offers to update the
:term:`asteroid name-number index<Asteroid name-number index>`. Further,
retrieves the current :term:`ssoCard` structure template from :term:`SsODNet`.
