.. _cli:

#####
Usage
#####

Most operations in ``rocks`` can be executed both via the command line and the
``python`` interface. The former is useful for quick data exploration, the
latter for a scripted data analysis. The available functions can generally be
divided into *identification*, *data exploration*, and *data analysis*.

Identification
==============

``rocks`` allows to quickly resolve the identity of asteroids, returning the current official designation and, if applicable, the number.
It recognizes aliases such as previously used provisional designations.

.. tab-set::

   .. tab-item:: Command Line

        The ``$ rocks id [identifier]`` command allows for quick name resolution via the command line.
        You can pass any valid asteroid :term:`identifier<Identifier>`. Note that whitespace and capitalization are irrelevant.

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


   .. tab-item:: python

        The ``rocks.id()`` function identifies one or many asteroids based on
        user-provided identifiers It is quite straight-forward: providing a
        single :term:`identifier <Identifier>` (or a list of many) returns a
        tuple containing the ``(asteroid name, asteroid number)`` (or a list of
        tuples).

        .. code-block:: python

            >>> import rocks
            >>> rocks.id(11334)
            ('Rio de Janeiro', 11334)
            >>> rocks.id(["SCHWARTZ", "J95X00A", "47", 3.])
            [('Schwartz', 13820), ('1995 XA', 24850), ('Aglaja', 47), ('Juno', 3)]

        .. admonition:: Hint
           :class: tip

           Note the alphabetical order: first returned is the **na**\me, then the **nu**\mber.

The command line offers more functionality related to identification of asteroids:

.. tab-set::

   .. tab-item:: Get Aliases

     .. _aliases:

     Using the plural ``ids`` returns the list of aliases under which the asteroid may be listed as well.

     .. code-block:: bash

        $ rocks ids aschera                                                                                     master
          (214) Aschera, aka
          ['1880 DB', '1903 SE', '1947 BP', '1948 JE', '1949 QG2', '1949 SX1',
           '1950 XH', '1953 OO', '2000214', 'I80D00B', 'J03S00E', 'J47B00P',
           'J48J00E', 'J49Q02G', 'J49S01X', 'J50X00H', 'J53O00O']

     All these aliases are automatically resolved to ``(214) Aschera`` by ``rocks`` using `quaero <https://ssp.imcce.fr/webservices/ssodnet/api/quaero/>`_.

   .. tab-item:: Citation Look-Up
     :selected:

     .. _who:

     Use ``$ rocks who`` to get the citations associated to each named asteroid.

     .. code-block:: bash

       $ rocks who zappafrank
       (3834) Zappafrank
          Named in memory of Frank Zappa (1940-1993), rock musician and composer [...]

   .. tab-item:: Search for Names

    If the ``fzf`` :ref:`tool is installed<install_fzf>`, executing the
    identification commands ``id|ids|who`` without passing and
    :term:`identifier <Identifier>` will launch an interactive search through
    all asteroids in the :term:`asteroid name-number index <Asteroid
    name-number index>`. In the example below, asteroid `(3834) Zappafrank` is
    selected interactively from all 1,218,250 recognised asteroid names:

    .. code-block:: bash

        $ rocks who

          (225250)  Georgfranziska
          (16127)   Farzan-Kashani
          (520)     Franziska
          (3183)    Franzkaiser
        > (3834)    Zappafrank

        > frank za  < 5/1218250

    Furthermore, ``rocks`` provides a hint for unidentified names with close matches in the :term:`asteroid name-number index <Asteroid name-number index>`.

    .. code-block:: bash

       $ rocks id barkajdetolli
       rocks: Could not find match for id Barkajdetolli.

       Could this be the rock you're looking for?
         (4524) Barklajdetolli

.. admonition:: Hint
   :class: tip

   Whitespace and capitalization are irrelevant for successful identification of the passed :term:`identifier <Identifier>`.


Data Exploration
================

The quick look-up of asteroid parameter values is most convenient via the command
line. The most general use case is to provide an asteroid parameter and
:term:`identifier<Identifier>` to echo the value from the :term:`ssoCard`.

.. tab-set::

   .. tab-item:: Command Line

        .. code-block:: sh

           $ rocks diameter pallas
           514.1 +- 3.906 km

   .. tab-item:: python

        .. code-block:: python

           >>> import rocks
           >>> pallas = rocks.Rock('pallas')
           >>> pallas.diameter.value
           514.1
           >>> pallas.diameter.error
           3.906
           >>> pallas.diameter.unit
           'km'

.. admonition:: Important
   :class: important

   All data that you look up is cached on your computer to increase the
   execution speed repeated queries. Remember to run ``$ rocks status`` to
   update or remove the cached data regularly (e.g. once a month) as there may
   be new observations available.

The parameter names follow the structure of the ssoCard. The different levels are connected
via dots, e.g. ``parameters.physical.albedo``. For convenience, ``parameters.physical`` and ``parameters.dynamical``
does not have to be specified.
For even more convenience, there are shortcuts defined for some parameters to reduce the amount of
typing, such as ``proper_elements.proper_semi_major_axis`` -> ``ap``, ``orbital_elements.orbital_period`` -> ``P``.


.. code-block:: sh

   $ rocks parameters.dynamical.orbital_elements.semi_major_axis ceres
   2.76661907 +- 0.00000010 au

   $ rocks orbital_elements.semi_major_axis ceres
   2.76661907 +- 0.00000010 au

   $ rocks a ceres
   2.76661907 +- 0.00000010 au

A complete list is given in the :ref:`appendix <parameter_aliases>`.\ [#f1]_

.. admonition:: Warning
   :class: warning

   Some parameter names (e.g. ``class``) are protected ``python`` keywords and can therefore not be
   used to refer to the asteroid parameter. These names carry a ``_``-suffix instead when using the ``python``
   interface:

   .. code-block:: python

     >>> import rocks
     >>> rocks.Rock(1).taxonomy.class_.value
     'C'

   The complete list of parameters which require the suffix is given in the :ref:`appendix <need_suffix>`.
   It contains all parameters for which the following evaluates to ``True``:

   .. code-block:: python

     >>> import keyword
     >>> keyword.iskeyword('class')
     True

.. admonition:: Another Warning
   :class: warning

   Some parameter names in the :ref:`ssoCard` are invalid variable names in ``python``,
   such as the name of colors (e.g. ``c-o``). In general, characters such
   as ``-``, ``/``, ``.``, are replaced by ``_`` in parameter names (e.g. ``c_o``).


Both the best-estimates stored in the :term:`ssoCard` and the literature compilation
of the parameters stored in the :term:`datacloud <Datacloud Catalogue>` are available for look-up.
In general, best-estimates are returned if the parameter is specified in singular form (e.g. `albedo`)
while all available data is returned for the plural form (e.g. `albedos`).

.. tab-set::

   .. tab-item:: Singular: ssoCard

        .. code-block:: sh

           $ rocks taxonomy aschera
           E

   .. tab-item:: Plural: datacloud

        .. code-block:: sh

           $ rocks taxonomies aschera
           +---+--------+---------+--------+-----------+-----------+-----------------+
           |   │ class_ | complex | method | waverange | scheme    | shortbib        |
           +---+--------+---------+--------+-----------+-----------+-----------------+
           | 1 | E      | E       | Phot   | VIS       | Tholen    | Tholen+1989     |
           | 2 | Xc     | X       | Spec   | VIS       | Bus       | Bus&Binzel+2002 |
           | 3 | B      | B       | Spec   | VIS       | Bus       | Lazzaro+2004    |
           | 4 | B      | B       | Spec   | VIS       | Tholen    | Lazzaro+2004    |
           | 5 | Cgh    | Ch      | Spec   | VISNIR    | Bus-DeMeo | DeMeo+2009      |
           | 6 | B      | B       | Spec   | VISNIR    | Bus       | deLeon+2012     |
           | 7 | C      | C       | Spec   | VISNIR    | Bus-DeMeo | deLeon+2012     |
           | 8 | B      | B       | Spec   | VISNIR    | Tholen    | deLeon+2012     |
           | 9 | E      | E       | Spec   | VISNIR    | Mahlke    | Mahlke+2022     |
           +---+--------+---------+--------+-----------+-----------+-----------------+

An overview of the available parameters is given in the :ref:`appendix
<parameter_names>`. Alternatively, you can run ``$ rocks parameters`` to echo
the template form of the :term:`ssoCard` in ``JSON`` format.

To echo the complete :term:`ssoCard` of an asteroid, use the ``$ rocks info`` command.

.. _getting_values:

Data Analysis
=============

To build an analysis around the asteroid data compiled in SsODNet, ``rocks`` provides
a ``python`` interface built around the ``Rock`` class. Each ``Rock`` object
represents an asteroid. They are created by passing an :term:`identifier <Identifier>`,
which is then resolved and the data corresponding to the asteroid is retrieved.

.. code-block:: python

    >>> import rocks
    >>> ceres = rocks.Rock(1)
    >>> ceres
    Rock(number=1, name='Ceres')
    >>> vesta = rocks.Rock("1807 FA")
    >>> vesta
    Rock(number=4, name='Vesta')

.. admonition:: Hint
   :class: tip

   Creating a large number of ``Rock`` objects can take a while if the requested data is not cached
   on the computer. Using the ``rocks.rocks()`` function drastically speeds up the process by first requesting
   all required data asynchronously from the SsODNet servers. See :ref:`this tutorial <rocksrocks>`.

All :term:`ssoCard` parameters are then available via the dot notation. The same shortcuts
as explained above are implemented.

.. code-block:: python

    >>> ceres.parameters.physical.taxonomy.class_.value
    'C'
    >>> ceres.taxonomy.class_.value
    'C'
    >>> ceres.a.value
    2.3615126


.. admonition:: Hint
   :class: tip

   Errors in the :ref:`ssoCard` are given as upper and lower value. They are accessed as described above:

   .. code-block:: python

       >>> ceres.diameter.error.min_
       0.4
       >>> ceres.diameter.error.max_
       -0.4

   To get the mean of the upper and lower error, you can use the ``error_`` attribute instead:

   .. code-block:: python

       >>> ceres.diameter.error_
       0.4

Access of ``datacloud`` tables
------------------------------

``datacloud`` catalogues of an asteroid are not loaded by default when creating
a ``Rock`` instance, as each table requires an additional remote query. Tables
are explicitly requested using the ``datacloud`` argument. Single tables can be
requested by passing the :ref:`table name <parameter_names>` to the ``datacloud``.

.. code-block:: python

    >>> ceres = rocks.Rock(1, datacloud='masses')

Multiple tables are retrieved by passing a list of table names.

.. code-block:: python

    >>> ceres = rocks.Rock(1, datacloud=['taxonomies', 'masses'])
    >>> ceres.taxonomies.class_
    ['G', 'C', 'C', 'C', 'C', 'G', 'C']
    >>> ceres.taxonomies.shortbib
    ['Tholen+1989', 'Bus&Binzel+2002', 'Lazzaro+2004', 'Lazzaro+2004',
     'DeMeo+2009', 'Fornasier+2014', 'Fornasier+2014']

.. _iterate_catalogues:

Once ingested into the ``Rock`` object, each catalogue is essentially a ``pandas.DataFrame``,
making operations such as accessing the catalogue values identical to the `standard pandas operations <https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html>`_.

.. code-block:: python

    >>> vesta = rocks.Rock(4, datacloud="diamalbedo")
    >>> for _, entry in vesta.diameters.iterrows():
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

.. _bibman:

Bibliography Management with ``rocks``
--------------------------------------

Giving credit where credit is due is straight-forward with ``rocks``: all parameters in the :term:`ssoCard`
and :term:`datacloud catalogues<Datacloud Catalogue>` contain their bibliographic references in the ``bibref``
entry. As values in the :term:`ssoCard` may be derived from multiple observations, the ``bibref`` attribute
of the ``Rock`` class parameters is a list.

.. tab-set::

   .. tab-item:: ssoCard

        .. code-block:: python

            >>> import rocks
            >>> pallas = rocks.Rock(2)
            >>> pallas.diameter.bibref
            [Bibref(doi='10.1051/0004-6361/202141781', year=2021, title='VLT/SPHERE imaging survey of the largest main-belt asteroids: Final results and synthesis', bibcode='2021A&A...654A..56V', shortbib='Vernazza+2021'),
             Bibref(doi='10.1016/j.icarus.2009.08.007', year=2010, title='Physical properties of (2) Pallas', bibcode='2010Icar..205..460C', shortbib='Carry+2010a'),
             Bibref(doi='10.1038/s41550-019-1007-5', year=2020, title='The violent collisional history of aqueously evolved (2) Pallas', bibcode='2020NatAs...4..569M', shortbib='Marsset+2020'),
              Bibref(doi='10.1051/0004-6361/201629956', year=2017, title='Volumes and bulk densities of forty asteroids from ADAM shape modeling', bibcode='2017A&A...601A.114H', shortbib='Hanuš+2017a')]


   .. tab-item:: datacloud

        Datacloud catalogues are serialized as ``pandas`` ``DataFrame``. The bibliographic information
        is provided the ``shortbib`` and ``bibcode`` attributes.

        .. code-block:: python

            >>> import rocks
            >>> pallas = rocks.Rock(2, datacloud='diameters')
            >>> pallas.diameters.columns
            Index(['title', 'shortbib', 'bibcode', 'year', 'id_', 'number', 'name',
                   'diameter', 'err_diameter_up', 'err_diameter_down', 'albedo',
                   'err_albedo_up', 'err_albedo_down', 'beaming', 'err_beaming',
                   'emissivity', 'err_emissivity', 'selection', 'method',
                   'preferred_albedo', 'preferred_diameter', 'preferred'],
                  dtype='object')
            >>> pallas.diameters.shortbib
            0                 Herald+2019
            1                 Herald+2019
            2                   Ryan+2010
            3               Drummond+2008
            4               Tedesco+2002a
            5               Drummond+1989
            6               Drummond+2009
            7               Vernazza+2021
            8                 Carry+2010a
            9                   Usui+2011
            10               Marsset+2020
                      [...]
            Name: shortbib, dtype: object

The ``shortbib`` attribute of the ``bibref`` entries gives a legible list of source publications. The
``bibcode`` or ``doi`` attributes may be useful for bibliographic management in TeX publications.

.. code-block:: python

   >>> import rocks
   >>> pallas = rocks.Rock(2)
   >>> shortbibs = pallas.diameter.bibref.shortbib
   >>> bibcodes = pallas.diameter.bibref.bibcode
   >>> print(f"The diameter of (2) Pallas is based on work by {', '.join(shortbibs)}")
   The diameter of (2) Pallas is based on work by Vernazza+2021, Carry+2010a, Marsset+2020, Hanuš+2017a)
   >>> print("To cite: \cite{",  ','.join(bibcodes), '}')
   To cite: \cite{ 2021A&A...654A..56V,2010Icar..205..460C,2020NatAs...4..569M,2017A&A...601A.114H }

To get a specific bibliographic reference, we select it based on its index from the ``bibref`` list:

.. code-block:: python

   >>> pallas.diameter.bibref[0]
   Bibref(
     doi='10.1051/0004-6361/202141781',
     year=2021,
     title='VLT/SPHERE imaging survey of the largest main-belt asteroids: Final results and synthesis',
     bibcode='2021A&A...654A..56V',
     shortbib='Vernazza+2021'
   )



Other use cases
---------------

.. _author:

Author and method look-up to be implemented.


.. rubric:: Footnotes
   :caption:

.. [#f1] Feel free to suggest a new alias via the `GitHub issues page <https://github.com/maxmahlke/rocks/issues>`_ if you find yourself typing too much.
