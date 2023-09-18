.. _cli:

###########
Basic Usage
###########

Most operations in ``rocks`` can be executed both via the command line and the
``python`` interface. The former is useful for quick data exploration, the
latter for a scripted data analysis. The available functions can generally be
divided into *identification*, *data exploration*, and *data analysis*.

.. _name_resolution:

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


.. _data_exploration:

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

.. _datacloud_example:

.. tab-set::

   .. tab-item:: Singular: ssoCard

        .. code-block:: sh

           $ rocks taxonomy aschera
           E

   .. tab-item:: Plural: datacloud
        :selected:

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

.. _masses_ceres:

.. code-block:: python

    >>> ceres = rocks.Rock(1, datacloud='masses')
    >>> len(ceres.masses.mass)  # 20 observations of Ceres' mass in database
    20
    >>> for i, obs in ceres.masses.iterrows():  # datacloud catalogues are pandas DataFrames
    >>>   mean_error = (obs.err_mass_up + abs(obs.err_mass_do wn)) / 2
    >>>   print(f"[{'X' if obs.preferred else ' '}] {obs.mass} +- {mean_error} [{obs.shortbib}, Method: {obs.method}]")
    [ ] 8.27e+20 +- 3.78e+19 [Kuzmanoski+1996, Method: DEFLECT]
    [ ] 8.73e+20 +- 7.96e+18 [Hilton+1999, Method: DEFLECT]
    [ ] 9.04e+20 +- 1.39e+19 [Kova+2012, Method: DEFLECT]
    [ ] 9.19e+20 +- 1.41e+19 [Sitarski+1995, Method: DEFLECT]
    [ ] 9.29e+20 +- 1.79e+19 [Carpino+1996, Method: DEFLECT]
    [ ] 9.29e+20 +- 3.68e+18 [Fienga+2013, Method: EPHEM]
    [ ] 9.29e+20 +- 3.84e+18 [Fienga+2014, Method: EPHEM]
    [ ] 9.31e+20 +- 6.46e+18 [Konopliv+2011, Method: EPHEM]
    [ ] 9.32e+20 +- 9.32e+19 [Folkner+2009, Method: EPHEM]
    [ ] 9.3483e+20 +- 5.967e+19 [Goffin1991, Method: DEFLECT]
    [ ] 9.35e+20 +- 5.57e+18 [Konopliv+2006, Method: DEFLECT]
    [ ] 9.35e+20 +- 5.97e+19 [Goffin+2001, Method: DEFLECT]
    [ ] 9.35e+20 +- 7.96e+18 [Michalak+2000, Method: DEFLECT]
    [ ] 9.38348e+20 +- 2.28689e+18 [Fienga+2019, Method: EPHEM]
    [X] 9.384e+20 +- 1e+17 [Russell+2016, Method: SPACE]
    [ ] 9.38e+20 +- 2.21e+18 [Viswanathan+2017, Method: EPHEM]
    [ ] 9.394e+20 +- 1.312e+18 [Baer+2017, Method: EPHEM]
    [ ] 9.39e+20 +- 1.57e+18 [Pitjeva+2013, Method: EPHEM]
    [ ] 9.39e+20 +- 2.31e+18 [Fienga+2020, Method: EPHEM]
    [ ] 9.39e+20 +- 5.97e+18 [Pitjeva+2010, Method: EPHEM]
    [ ] 9.40797e+20 +- 0.0 [Folkner+2014, Method: EPHEM]
    [ ] 9.41e+20 +- 5.69e+18 [Kuchynka+2013, Method: EPHEM]
    [ ] 9.42e+20 +- 2.65e+18 [Zielenbach+2011, Method: DEFLECT]
    [ ] 9.42e+20 +- 2.68e+18 [Zielenbach+2011, Method: DEFLECT]
    [ ] 9.42e+20 +- 5.17e+18 [Kova+2007, Method: DEFLECT]
    [ ] 9.44e+20 +- 5.97e+17 [Goffin+2014, Method: DEFLECT]
    [ ] 9.45e+20 +- 3.98e+18 [Pitjeva+2004, Method: DEFLECT]
    [ ] 9.45e+20 +- 4.18e+18 [Pitjeva+2005, Method: EPHEM]
    [ ] 9.45e+20 +- 5.97e+18 [Baer+2008a, Method: DEFLECT]
    [ ] 9.46366e+20 +- 5.5692e+18 [Fienga+2011, Method: EPHEM]
    [ ] 9.46e+20 +- 1.43e+18 [Baer+2011, Method: DEFLECT]
    [ ] 9.46e+20 +- 7.96e+17 [Fienga+2008, Method: EPHEM]
    [ ] 9.47e+20 +- 4.57e+18 [Viateau+1998, Method: DEFLECT]
    [ ] 9.4e+20 +- 3.1e+18 [Zielenbach+2011, Method: DEFLECT]
    [ ] 9.52e+20 +- 4.63e+18 [Zielenbach+2011, Method: DEFLECT]
    [ ] 9.52e+20 +- 7.76e+18 [Viateau+1997b, Method: DEFLECT]
    [ ] 9.54e+20 +- 1.69e+19 [Sitarski+1992, Method: DEFLECT]
    [ ] 9.55e+20 +- 4.38e+19 [Williams+1992, Method: DEFLECT]
    [ ] 9.57e+20 +- 1.99e+18 [Pitjeva+2001, Method: DEFLECT]
    [ ] 9.94e+20 +- 3.98e+19 [Viateau+1995, Method: DEFLECT]

.. Note::

    As the ``diamalbedo`` catalogue contains both diameters and albedos, it contains the ``preferred_diameter`` and ``preferred_albedo`` attributes.

``rocks`` offers an easy way to compute the weighted averages of the preferred property measurements, see for example: :ref:`what's the weighted average albedo of (6) Hebe?<weighted_average_scripted>`

.. _bft_example:

Access of ``ssoBFT``
--------------------

The `ssoBFT <https://ssp.imcce.fr/webservices/ssodnet/api/ssobft/>`_ contains all best-estimate parameters
of all known minor bodies in SsODNet. It aggregates 591 of about 1,200,000 objects. For quick execution times, `rocks`
stores the ``parquet`` version (~600MB) of the ssoBFT in the cache directory when it is first requested
via the ``rocks.load_bft()`` function. The returned table is a ``pandas`` ``DataFrame`` and enables quick sample selection
via minor body parameters.


.. code-block:: python

   >>> import rocks
   >>> bft = rocks.load_bft()
   >>> family_eos = bft[bft['family.family_name'] == 'Eos']
   >>> family_eos['albedo.value'].mean()
   0.12367009372337404

To get the advantages of the ``Rock`` class, you can pass any subset of the ssoBFT to ``rocks.rocks``. To get all asteroids in the family of (121) Hermione:

.. code-block:: python

   >>> family_hermione = bft[bft['family.family_name'] == 'hermione']  # pd.DataFrame
   >>> family_hermione = rocks.rocks(family_hermione)  # list of Rock instances
   >>> family_hermione
   [Rock(number=121, name='Hermione'),
    Rock(number=168, name='Sibylla'),
    Rock(number=2634, name='James Bradley'),
    Rock(number=4003, name='Schumann'),
    ...
   ]

Or all asteroids in the Vesta family larger than 5km in diameter and with a taxonomic classification:

.. code-block:: python

   >>> subset_vesta = bft[(bft['family.family_name'] == 'Vesta') & (bft['diameter.value'] > 5) & (~pd.isna(bft['taxonomy.class']))]
   >>> subset_vesta = rocks.rocks(subset_vesta)  # list of 82 Rocks

The valid column names for the selection are given on the `ssoBFT API <https://ssp.imcce.fr/webservices/ssodnet/api/ssobft/>`_ page.

Column Selection
++++++++++++++++

The BFT is a large, sparse table containing many columns that you might not
need routinely. On some machines, loading the entire table may further exceed
the memory size and lead to crashes.

To reduce its size in memory and the time to load it, ``rocks`` by default
only loads a :ref:`subset of the available columns<lite_columns>`.
You can define your own subset of columns by setting
``rocks.bft.COLUMNS`` to the list of the desired columns

.. code-block:: python

   >>> rocks.bft.COLUMNS = ['sso_number', 'diameter.value', 'mass.value', 'taxonomy.class', 'family.family_status']
   >>> rocks.load_bft()  # loads rocks.bft.COLUMNS by default

Alternatively, you can directly pass the list to the ``columns`` keyword argument:

   >>> rocks.load_bft(columns=['sso_number', 'diameter.value', 'mass.value', 'taxonomy.class', 'family.family_status'])

You can request the full table using the ``full`` keyword argument (though it's not recommended):

.. code-block:: python

   >>> bft = rocks.load_bft(full=True)

.. rubric:: Footnotes

.. [#f1] Feel free to suggest a new alias via the `GitHub issues page <https://github.com/maxmahlke/rocks/issues>`_ if you find yourself typing too much.
