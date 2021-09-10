.. _rock_class:

``rocks`` provides object-oriented access to the data stored in ssoCards and
datacloud. The implementation focuses on ease of access and speed: all
attributes are accessible via the common dot notation, and queries to
``SsODNet`` are run asynchronously.

The public API only consists of two functions and one class:

- ``rocks.identify()``: identify one or many asteroids based on user-provided identifiers

- ``rocks.Rock``: each ``Rock`` represents one asteroid and contains the data of its ``ssoCard``

- ``rocks.rocks()``: a wrapper around ``rocks.identify()`` and ``rocks.Rock`` to read in the data of many asteroids

Identification of asteroids
===========================

It is quite straight-forward: providing a single identifier or a list of many identifiers returns a tuple of ``(asteroid name, asteroid number)`` for each
identifier. Identifiers can be ``floats``, ``integers``, or ``strings`` and can describe the asteroid's name, number, designation, previous designations,
packed designations, and more.

.. code-block:: python

    >>> from rocks.identify import identify
    >>> rocks.identify(11334)
    ('Rio de Janeiro', 11334)
    >>> rocks.identify(["SCHWARTZ", "J95X00A", "47", 3.])
    [('Schwartz', 13820), ('1995 XA', 24850), ('Aglaja', 47), ('Juno', 3)]

It can be difficult to remember if the first item in the tuple is the asteroid name or number. A donkey bridge: it is returned in alphabetical order, first name, then number.

The ``Rock`` class
==================

The :ref:`Rock<rocks-Rock>` class is used to inspect the parameters of a single
asteroid. It is the (iron) core of the ``rocks`` package.

Creating a ``Rock`` instance
----------------------------

``Rocks`` are created by passing the name, number, or SsODNet ID of the asteroid that they should represent.

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

More shortcuts are :ref:`given below<attribute_shortcuts>`. Feel free to suggest new ones by opening an issue on the `GitHub page<https://github.com/maxmahlke/rocks`_.

Differences to the ``ssoCard`` structure arise in two cases:

- the ``ssoCard`` uses keywords which are protected in ``python``, such as the ``class`` keyword. These keywords have an underscore appended to them: ``class``, ``id``, ``min``, ``max``

- the ``ssoCard`` uses keywords which are invalid variable names in ``python``, such as the name of colours: "c-o" becomes "c_o". In general, characters such as ``-``, ``/``, ``.``, are replaced by ``_`` in parameter names.


Access of ``datacloud`` tables
------------------------------

The ``datacloud`` catalogues of an asteroid are not loaded by default when creating a
``Rock`` instance, as each table requires an additional remote query. Tables can
be requested using the ``datacloud`` argument instead.
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

Some observations in the catalogues might be preferred to others. For example, a
taxonomical classification using a visible-near-infrared spectrum is more
reliable than one based on visible colours. ``rocks`` includes **opinonated**
selections of preferred observations based on the observation methods, just as
the ``ssoCard`` does.  Catalogues have ``preferred`` attributes, which are lists
containing ``True`` if the corresponding observation is preferred, and ``False``
otherwise.

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

Special use-cases
-----------------

When passing the name or number, the asteroid is identified using
``rocks.identify()``. If the SsODNet ID of the asteroid is
provided, this check can be skipped by setting the ``skip_id_check`` argument to
``True``. This saves time when creating many ``Rock`` instances in a loop, as demonstrated in the :ref:`Tutorials<Tutorials>`.

.. code-block:: python

    >> mars_crosser_2016fj = Rock("2016_FJ", skip_id_check=True)

The user can further provide their own custom ssoCard to populate the ``Rock`` attributes.
The ``ssocard`` argument accepts a ``dict``ionary structure following the one of the
original ssoCards. The easiest way to achieve this is to edit a real ssoCard from SsODNet
and load it via the ``json`` module.

.. code-block:: python

    >>> import json
    >>> import os
    >>> with open("my_ssocard.json", "r") as file_:
    >>>    data = json.load(file_)
    >>> mars_crosser_2016fj = Rock("2016_FJ", ssocard=data["2016_FJ"])

.. _attribute_shortcuts:

List of attribute shortcuts
---------------------------

+------------------------+-------------------------+
| ssoCard attribute      | Shortcut                |
+------------------------+-------------------------+
| parameters.dynamical   | ````                    |
+------------------------+-------------------------+
| parameters.physical    | ````                    |
+------------------------+-------------------------+
| semi_major_axis        | ``a``                   |
+------------------------+-------------------------+
| eccentricity           | ``e``                   |
+------------------------+-------------------------+
| inclination            | ``i``                   |
+------------------------+-------------------------+
| proper_semi_major_axis | ``ap``                  |
+------------------------+-------------------------+
| proper_eccentricity    | ``ep``                  |
+------------------------+-------------------------+
| proper_inclination     | ``ip``                  |
+------------------------+-------------------------+

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
