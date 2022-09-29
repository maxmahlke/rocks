.. _cli:

#####
Usage
#####

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

.. _getting_values:

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

.. _datacloud:

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

.. _name_resolution:

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

.. _aliases:

Using the plural ``ids`` returns the list of aliases under which the asteroid may be listed as well.

.. code-block:: bash

   $ rocks ids aschera                                                                                     master
     (214) Aschera, aka
     ['1880 DB', '1903 SE', '1947 BP', '1948 JE', '1949 QG2', '1949 SX1',
      '1950 XH', '1953 OO', '2000214', 'I80D00B', 'J03S00E', 'J47B00P',
      'J48J00E', 'J49Q02G', 'J49S01X', 'J50X00H', 'J53O00O']

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


.. _rock_class:

The ``python`` Package
======================

``rocks`` provides object-oriented access to the data stored in :term:`ssoCards <ssoCard>` and
:term:`datacloud catalogues<Datacloud Catalogue>`. The implementation focuses on ease-of-access and speed: all attributes are accessible via the common dot notation, and queries to
:term:`SsODNet` are run asynchronously.

The public API only consists of two functions and one class:

- ``rocks.identify()``: identify one or many asteroids based on user-provided identifiers

- ``rocks.Rock``: each ``Rock`` represents one asteroid and contains the data of its :term:`ssoCard`

- ``rocks.rocks()``: a wrapper around ``rocks.identify()`` and ``rocks.Rock`` to read in the data of many asteroids

Identification of asteroids
===========================

It is quite straight-forward: providing a single :term:`identifier <Identifier>`
(or a list of many) returns a tuple containing the ``(asteroid name, asteroid number)`` (or a list of tuples).

.. code-block:: python

    >>> import rocks
    >>> rocks.identify(11334)
    ('Rio de Janeiro', 11334)
    >>> rocks.identify(["SCHWARTZ", "J95X00A", "47", 3.])
    [('Schwartz', 13820), ('1995 XA', 24850), ('Aglaja', 47), ('Juno', 3)]

Note the alphabetical order: first returned is the **na**\me, then the **nu**\mber.

.. _rock_class:

The ``Rock`` class
==================

The ``Rock`` class is used to inspect the parameters of a single
asteroid. It is the (iron) core of the ``rocks`` package.

Creating a ``Rock`` instance
----------------------------

``Rocks`` are created by passing the name, number, or :term:`SsODNet ID` of the asteroid that they should represent.

.. code-block:: python

    >>> from rocks import Rock
    >>> ceres = Rock(1)
    >>> ceres
    Rock(number=1, name='Ceres')
    >>> vesta = Rock("1807 FA")
    >>> vesta
    Rock(number=4, name='Vesta')

Access of ssoCard parameters
----------------------------

During instantiation, the asteroid properties are retrieved from ``SsODNet`` and assigned to the attributes following the structure of the ``ssoCard``.

.. code-block:: python

    >>> ceres.parameters.physical.taxonomy.class_
    C
    >>> vesta.parameters.dynamical.proper_elements.proper_semi_major_axis.value
    2.3615126

Notice the ``.value`` suffix to retrieve the value of numerical parameters, just as in an ``ssoCard`` itself.

To reduce the typing effort, the ``parameters`` and ``physical``/ ``dynamical``
attributes can be skipped.

.. code-block:: python

   >>> vesta.parameters.physical.diameter
   525.4
   >>> vesta.diameter
   525.4

More shortcuts are :ref:`given below<attribute_shortcuts>`. Feel free to suggest new ones by opening an issue on the `GitHub page <https://github.com/maxmahlke/rocks>`_.

Differences to the ``ssoCard`` structure arise in two cases:

- the ``ssoCard`` uses keywords which are protected in ``python``, such as the ``class`` keyword. These keywords have an underscore appended to them: ``class``, ``id``, ``min``, ``max``

- the ``ssoCard`` uses keywords which are invalid variable names in ``python``, such as the name of colours: "c-o" becomes "c_o". In general, characters such as ``-``, ``/``, ``.``, are replaced by ``_`` in parameter names.

 .. TODO Document the errors_ attribute of the Values class

Access of ``datacloud`` tables
------------------------------

The ``datacloud`` catalogues of an asteroid are not loaded by default when creating a
``Rock`` instance, as each table requires an additional remote query. Tables can
be requested using the ``datacloud`` argument instead.
Single tables can be requested by passing the table name to the ``datacloud``.

.. code-block:: python

    >>> ceres = Rock(1, datacloud='masses')

Multiple tables are retrieved by passing a list of table names.

.. code-block:: python

    >>> ceres = Rock(1, datacloud=['taxonomies', 'masses'])
    >>> ceres.taxonomies.class_
    ['G', 'C', 'C', 'C', 'C', 'G', 'C']
    >>> ceres.taxonomies.shortbib
    ['Tholen+1989', 'Bus&Binzel+2002', 'Lazzaro+2004', 'Lazzaro+2004',
     'DeMeo+2009', 'Fornasier+2014', 'Fornasier+2014']

.. _iterate_catalogues:

From a ``python`` view, the catalogues are subclassed of the ``pandas.DataFrame``.
As such, the catalogues are iterable and return a catalogue per entry in each iteration.

.. code-block:: python

    >>> vesta = Rock(4, datacloud="diamalbedo")
    >>> for entry in vesta.diameters:
            print(f"{entry.diameter:.1f}km, observed via {entry.method} by {entry.shortbib}")

    507.3km, observed via TE-IM by Drummond+1998
    530.0km, observed via STM by Morrison+2007
    510.0km, observed via TE-IM by Drummond+2008
    468.3km, observed via STM by Tedesco+2001
    520.4km, observed via STM by Ryan+2010
    515.9km, observed via NEATM by Ryan+2010
    521.7km, observed via NEATM by Usui+2011
    525.4km, observed via SPACE by Russell+2012
    562.6km, observed via NEATM by Alí-Lagoa+2018
    505.4km, observed via OCC by Herald+2019
    522.0km, observed via OCC by Herald+2019

Other convenient ``DataFrame`` methods such as ``groupby`` are also available. The difference between the ``DataCloudDataFrame`` and the original ``DataFrame`` are two added methods for the former: ``weighted_average`` and ``plot``.


The ``datacloud`` tables have slightly different names in ``rocks``.

+-----------------+----------------------------+
| datacloud Table | Attribute Name             |
+-----------------+----------------------------+
| aams            | ``aams``                   |
+-----------------+----------------------------+
| astdys          | ``astdys``                 |
+-----------------+----------------------------+
| astorb          | ``astorb``                 |
+-----------------+----------------------------+
| binarymp_tab    | ``binaries``               |
+-----------------+----------------------------+
| diamalbedo      | ``diamalbedo``             |
+-----------------+----------------------------+
| families        | ``families``               |
+-----------------+----------------------------+
| masses          | ``masses``                 |
+-----------------+----------------------------+
| mpcatobs        | ``mpc``                    |
+-----------------+----------------------------+
| pairs           | ``pairs``                  |
+-----------------+----------------------------+
| taxonomy        | ``taxonomies``             |
+-----------------+----------------------------+

Some attributes are called different in ``rocks`` than in the ``datacloud`` table:


The ``datacloud`` tables have slightly different names in ``rocks``.

+-----------------+----------------------------+
| datacloud Table | Attribute Name             |
+-----------------+----------------------------+
| num             | ``number``                 |
+-----------------+----------------------------+
| sibling_num     | ``sibling_number``         |
+-----------------+----------------------------+
| id              | ``id_``                    |
+-----------------+----------------------------+
| lambda          | ``lambda_``                |
+-----------------+----------------------------+
| class           | ``class_``                 |
+-----------------+----------------------------+
| from           | ``from_``                   |
+-----------------+----------------------------+

Some observations in the catalogues might be preferred to others. For example, a
taxonomical classification using a visible-near-infrared spectrum is more
reliable than one based on visible colours. ``rocks`` includes **opinionated**
selections of preferred observations based on the observation methods, just as
the ``ssoCard`` does.  Catalogues have ``preferred`` attributes, which are lists
containing ``True`` if the corresponding observation is preferred, and ``False``
otherwise.

.. code-block:: python

    >>> ceres = Rock(1, datacloud='masses')
    >>> len(ceres.masses.mass)  # 20 observations of Ceres' mass in database
    20
    >>> for obs in ceres.masses:
          if obs.preferred:
              print(f"Mass: {obs.mass}, Method: {obs.method}, from {obs.shortbib}")
    Mass: 9.384e+20, Method: SPACE, from Russell+2016

.. Note::

    As the ``diamalbedo`` catalogue contains both diameters and albedos, it contains the ``preferred_diameter`` and ``preferred_albedo`` attributes.

``rocks`` offers an easy way to compute the weighted averages of the preferred property measurements, see for example: :ref:`what's the weighted average albedo of (6) Hebe?<weighted_average_scripted>`

Special use-cases
-----------------

When passing the name or number, the asteroid is identified using
``rocks.identify()``. If the SsODNet ID of the asteroid is
provided, this check can be skipped by setting the ``skip_id_check`` argument to
``True``. This saves time when creating many ``Rock`` instances in a loop, as demonstrated in the :ref:`Tutorials<Tutorials>`.

.. code-block:: python

    >>> mars_crosser_2016fj = Rock("2016_FJ", skip_id_check=True)

The user can further provide their own custom ssoCard to populate the ``Rock`` attributes.
The ``ssocard`` argument accepts a ``dict``\ ionary structure following the one of the
original ssoCards. The easiest way to achieve this is to edit a real ssoCard from SsODNet
and load it via the ``json`` module.

.. code-block:: python

    >>> import json
    >>> import os
    >>> with open("my_ssocard.json", "r") as file_:
    >>>    data = json.load(file_)
    >>> mars_crosser_2016fj = Rock("2016_FJ", ssocard=data["2016_FJ"])

Creating many ``Rock``\ s
=========================

The ``rocks.rocks()`` function serves as a one-line replacement for a frequent approach: get a list of asteroid identifiers from a catalogue and create ``Rock`` instances from them.

.. code-block:: python

    >>> from rocks import rocks
    >>> themis_family = [24, 62, 90, 104, 171, 222, 223, 316, 379,
                         383, 468, 492, 515, 526, 767, 846]
    >>> themis_family = rocks(themis_family)
    >>> themis_family
    [Rock(number=316, name='Goberta'), Rock(number=492, name='Gismonda'),
    Rock(number=767, name='Bondia'), Rock(number=90, name='Antiope'), ... ]

Accessing the properties can now be done with a loop or list comprehension.

    >>> from collections import Counter
    >>> themis_taxonomies = [t.taxonomy.class_ for t in themis_family]
    >>> Counter(themis_taxonomies)
    Counter({'C': 8, 'B': 2, 'Ch': 2, 'BU': 1, 'Xc': 1, 'Xk': 1, 'Cb': 1})

Any property not present in the ssoCard of an asteroid is set to ``NaN``. This ensures that accessing attributes in a loop does not fail.

.. _who:

Use ``$ rocks who`` to get the citations associated to each named asteroid.

.. _author:

Author look-up to be implemented.
