.. _rock_class:

The ``Rock`` class
==================

The :ref:`Rock<rocks-Rock>` class is used to inspect the properties of a single asteroid. The asteroid is specified by providing its number, name, or designation to the class.

Creating a ``Rock`` instance
----------------------------

``Rocks`` are created by passing the name, number, or SsODNet ID of the asteroid that they
should represent.

.. code-block:: python

    >> from rocks import Rock
    >> ceres = Rock(1)
    >> ceres
    Rock(number=1, name='Ceres')
    >> vesta = Rock("1807 FA")
    >> vesta
    Rock(number=4, name='Vesta')

When passing the name or number, the asteroid is identified using the
``rocks.identify()`` ``quaero`` frontend. If the SsODNet ID of the asteroid is
provided, this check can be skipped by setting the ``skip_id_check`` argument to
``True``. This saves time when creating many ``Rock`` instances in a loop, as demonstrated
in the :ref:`Tutorials<Tutorials>`.

.. code-block:: python

    >> mars_crosser_2016fj = Rock("2016_FJ", skip_id_check=True)

The user can further provide their own custom ssoCard to populate the ``Rock`` attributes.
The ``ssocard`` argument accepts a ``dict``ionary structure following the one of the
original ssoCards. The easiest way to achieve this is to edit a real ssoCard from SsODNet
and load it via the ``json`` module.

.. code-block:: python

    >> import json
    >> import os
    >> with open("my_ssocard.json", "r") as file_:
    >>    data = json.load(file_)
    >>
    >> mars_crosser_2016fj = Rock("2016_FJ", ssocard=data["2016_FJ"])

Access of ssoCard parameters
----------------------------

During instantiation, the asteroid properties are retrieved from `SsODNet <https://ssp.imcce.fr/webservices/ssodnet/>`_ and assigned to the attributes following the structure of the ``ssoCard``.

.. code-block:: python

    >> ceres.parameters.physical.taxonomy.class_
    C
    >> vesta.parameters.dynamical.proper_elements.proper_semi_major_aixs
    2.3615126

To reduce wordiness, the ``parameters`` and ``physical``/``dynamical`` attributes can be skipped. Units and uncertainties can be appended to the property.

.. code-block:: python

   >> vesta.parameters.physical.diameter
   468.3
   >> vesta.diameter
   468.3
   >> vesta.diameter.unit
   'km'

In general, the ``Rock`` attribute structure mimics the ssoCard structure as closely as possible.

Most differences arise due to the ssoCard using keywords which are protected in ``python`` and as such cannot be assigned, such as the ``class`` keyword. These keywords have an underscore appended to them, see the table below.

Another difference arises from keywords which are invalid variable names in ``python``, such as the name of colours: "c-o" becomes "c_o". In general, characters such as ``-``, ``/``, ``.``, are replaced by ``_`` in parameter names.

A chosen difference is the structure of the "method" and "bibref" values: when ingested into the ``Rock`` attribute, they are always a ``python`` ``list`` instance filled with one or more ``dict``. This is to simplify the code and prevent if-clauses.

Here is a list of ssoCard parameters and their corresponding names in the ``Rock`` instance if the names differ from one another.

+-----------------+----------------------------+
| ssoCard Name    | ``Rock`` attribute         |
+-----------------+----------------------------+
| class           | ``class_``                 |
+-----------------+----------------------------+
| id              | ``id_``                    |
+-----------------+----------------------------+
| min             | ``min_``                   |
+-----------------+----------------------------+
| max             | ``max_``                   |
+-----------------+----------------------------+


Access of ``datacloud`` tables
------------------------------

SsODNet:datacloud contains tables of albedos, masses, taxonomic classes and more
for a large number of asteroids. By default, they are not loaded when creating a
``Rock`` instance, as each table requires an additional remote query. Tables can
be requested using the ``datacloud`` argument, using the catalogues given in the
left column of the table below. They are assigned to the attributes given in the
right column.

+-----------------+----------------------------+
| Datacloud Table | Attribute Name             |
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

Single tables can be requested by passing the table name to the ``datacloud``.

.. code-block:: python

    >> ceres = Rock(1, datacloud='masses')

Multiple tables are retrieved by passing a list of table names.

.. code-block:: python

    >> ceres = Rock(1, datacloud=['taxonomy', 'masses'])
    >> ceres.taxonomies.class_
    ['G', 'C', 'C', 'C', 'C', 'G', 'C']
    >> ceres.taxonomies.shortbib
    ['Tholen+1989', 'Bus&Binzel+2002', 'Lazzaro+2004', 'Lazzaro+2004',
     'DeMeo+2009', 'Fornasier+2014', 'Fornasier+2014']

If the properties are of type ``float``, methods for :ref:`weighted averaging<rocks-wa>` and :ref:`plotting<rocks-plots>` are available.

.. code-block:: python

    >> ceres.masses.mass
    [9.55e+20, 9.54e+20, 9.94e+20, 9.19e+20, ..., 9.39e+20]
    >> ceres.masses.mass.weighted_average(errors=ceres.masses.err_mass)
    (9.387431170184913e+20, 3.282260016750655e+17)
    >> ceres.masses.scatter('mass', show=True)

The last line above will open a ``matplotlib`` scatterplot of the ``mass`` values in the ``masses`` catalogue. For the ``diamalbedo`` catalogue, both ``albedo`` and ``diameters`` can be specified.

.. Note::

   The units and uncertainties are not appended to properties in the datacloud catalgoues. This may be implemented in a later version.

Some observations in the catalogues might be preferred to others. For example, a taxonomical classification using a visible-nearinfrared spectrum is more reliable than one based on visible colours. ``rocks`` includes **opinonated** selections of preferred observations based on the observation methods. Catalogues have ``preferred`` attributes, which are lists containing ``True`` if the corresponding observation is preferred, and ``False`` otherwise.

.. code-block:: python

    >> ceres = Rock(1, datacloud='masses')
    >> len(ceres.masses.mass)  # 20 observations of Ceres' mass in database
    20
    >> for obs in ceres.masses:
          if obs.preferred:
              print(f"Mass: {obs.mass}, Method: {obs.method}, from {obs.shortbib}")
    Mass: 9.384e+20, Method: SPACE, from Russell+2016

.. Note::

    As the ``diamalbedo`` catalogue contains both diameters and albedos, it contains the ``preferred_diameter`` and ``preferred_albedo`` attributes.

``rocks`` offers an easy way to compute the weighted averages of the preferred property measurements, see for example: :ref:`what's the weighted average albedo of (6) Hebe?<weighted_average_scripted>`

Creating many ``Rock``\ s
-------------------------

The :ref:`rocks.rocks()<rocks-rocks>` function quickly creates many ``Rock`` instances. It accepts a list of asteroid numbers, names, or designations and returns a list of ``Rock`` instances.

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

.. Note::

  ssoCards are cached for shorter execution times. The cache directory is ``$HOME/.cache/rocks/``.

In the :ref:`Tutorials<Tutorials>` we show how to utilise ``rocks()`` to investigate the taxonomic distribution of asteroids in large catalogues. 


-------------------

API of ``Rock`` and ``rocks``
-----------------------------

.. _rocks-Rock:

.. currentmodule:: core

.. autoclass:: Rock

.. automethod:: Rock.__init__


.. _rocks-rocks:

.. currentmodule:: core

.. autofunction:: rocks


.. _rocks-wa:

.. currentmodule:: core

.. autofunction:: core.listSameTypeParameter.weighted_average

.. _rocks-plots:

.. autofunction:: core.propertyCollection.hist

.. autofunction:: core.propertyCollection.scatter


