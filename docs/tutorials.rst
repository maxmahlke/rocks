#########
Tutorials
#########

.. role:: raw-html(raw)
    :format: html

Below are some frequent analysis questions that ``rocks`` aims to solve
quickly. Do you have a good example to add? Post it in an issue on `GitHub
<https://github.com/maxmahlke/rocks/issues>`_.

Identification
--------------

.. dropdown:: How do I identify an asteroid?

   The  basic usage is shown below. More information can be found
   :ref:`here<cli_id>` and :ref:`here<Identification of asteroids>`.

   .. tab-set::

      .. tab-item:: Command Line

        .. code-block:: bash

          $ rocks id this
          (23) This

      .. tab-item:: python

        .. code-block:: python

          >>> rocks.id(['this', 'that'])
          [(this, 23), (that, 23)]


.. dropdown:: How do I ensure that the names and numbers of all asteroids in a file are up-to-date?

   Let's assume that the data file is in CSV format and that there is a single
   column ``designation`` which contains the :term:`identifiers<Identifier>` of
   the asteroids. These can be mixed: numbers, names, provisional designations
   in different formats.

   .. tab-set::

      .. tab-item:: python

       .. code-block:: python

         import pandas as pd
         import rocks

         data = pd.read_csv("/path/to/data.csv")

         # Assuming that the asteroid names and designations are in a column called "designation"
         data["name"] = [name for name, number in rocks.id(data["designation"])]

         # To update the numbers, just change the list comprehension
         data["number"] = [number for name, number in rocks.id(data["designation"])]


       Note that this solution is easy to code but inefficient as the
       identification is executed twice. The more efficient but less readable
       solution is

       .. code-block:: python

          data["name"], data["number"] = zip(*rocks.id(data["designation"]))

      .. tab-item:: Command Line

        Not possible. If you think it should be, open a feature request on `GitHub <https://github.com/maxmahlke/rocks/issues>`_.


.. - :ref:`Instead of a list of tuples, how can I get the list of resolved asteroid names from my identifiers? <>`

.. dropdown:: How can I get the aliases of an asteroid?

   .. tab-set::

      .. tab-item:: Command Line

       .. code-block:: bash

         $ rocks ids aschera
         (214) Aschera, aka
           ['1880 DB', '1903 SE', '1947 BP', '1948 JE', '1949 QG2', '1949 SX1', '1950 XH', '1953 OO',
            '2000214', 'I80D00B', 'J03S00E', 'J47B00P', 'J48J00E', 'J49Q02G', 'J49S01X', 'J50X00H', 'J53O00O']

      .. tab-item:: python

        Not possible. If you think it should be, open a feature request on `GitHub <https://github.com/maxmahlke/rocks/issues>`_.

.. dropdown:: What asteroids are in the SDSS MOC1?

   The script below shows the typical workflow of downloading a database of
   asteroid observations and updating the outdated provisional designations used
   to identify the asteroids.

   .. code-block:: python

       import numpy as np
       import pandas as pd
       import rocks

       # ------
       # Download SDSS MOC1 (28.6MB)
       data = pd.read_fwf(
           "https://faculty.washington.edu/ivezic/sdssmoc/ADR1.dat",
           colspecs=[(244, 250), (250, 270)],
           names=["numeration", "designation"],
       )

       print(f"Number of observations in SDSS MOC1: {len(data)}")

       # Remove the unknown objects
       data = data[data.designation.str.strip(" ") != "-"]
       print(f"Observations of known objects: {len(set(data.designation))}")

       # ------
       # Get current designations and numbers for objects

       # Unnumbered objects should be NaN
       data.loc[data.numeration == 0, "numeration"] = np.nan

       # Create list of identifiers by merging 'numeration' and 'designation' columns
       ids = data.numeration.fillna(data.designation)
       print("Identifying known objects in catalogue..")
       names_numbers = rocks.identify(ids)

       # Add numbers and names to data
       data["name"] = [name_number[0] for name_number in names_numbers]
       data["number"] = [name_number[1] for name_number in names_numbers]

       data.number = data.number.astype("Int64")  # Int64 supports integers and NaN
       print(data.head())

Data Exploration
----------------

.. dropdown:: How do I get best-estimates of asteroid parameters?

   The basic usage is shown below. More information can be found :ref:`here<Data Exploration>`.

   .. tab-set::

      .. tab-item:: Command Line

        The basic usage is ``$ rocks [parameter] [identifier]``. The list of
        valid parameter names can be found :ref:`here
        <rocks-props>`.

        .. code-block:: bash

          $ rocks albedo cybele
          0.0344 +- 0.2499

          $ rocks albedo.bibref ceres
          [Bibref(doi='10.3847/2041-8205/817/2/L22', year=2016, title='Surface Albedo and Spectral Variability of Ceres', bibcode='2016ApJ...817L..22L', shortbib='Li+2016')]

      .. tab-item:: python

        The asteroid parameters are accessed on a per-asteroid basis using the
        ``Rock`` class. All parameters from the :term:`ssoCard` are exposed via
        the simple dot notation. More information can be found :ref:`here <rock_class>`.

        .. code-block:: python

          >>> from rocks import Rock
          >>> pallas = rocks.Rock('pallas')
          >>> pallas.albedo.value
          0.1512


.. dropdown:: How do I get all the taxonomic classes proposed for Ceres?

  The taxonomic classes assigned to minor planets in public literature are available in the ``taxonomies`` :ref:`datacloud catalogues <Datacoud Catalogue>`. They can be retrieved via the command line
  and in a ``python`` script as :ref:`DataCloudDataFrame` instance.

  .. tab-set::

    .. tab-item:: Command Line

      .. code-block:: bash

        $ rocks taxonomies Ceres

    .. tab-item:: python

      .. code-block:: python

       >>> import rocks
       >>> ceres = rocks.Rock(1, datacloud="taxonomies")
       >>> for index, classification in ceres.taxonomies.iterrows():
               print(f"{classification.shortbib} assigned class {classification.class_} to Ceres")

       Tholen+1989 assigned class G to Ceres
       Bus&Binzel+2002 assigned class C to Ceres
       Lazzaro+2004 assigned class C to Ceres
       Lazzaro+2004 assigned class C to Ceres
       DeMeo+2009 assigned class C to Ceres
       Fornasier+2014 assigned class G to Ceres
       Fornasier+2014 assigned class C to Ceres
       Mahlke+2022 assigned class C to Ceres


.. dropdown:: How do I get the taxonomy distribution of the first 1000 numbered minor planets?

    .. code-block:: python

       #!/usr/bin/env python
       """Retrieve taxonomies of first 1000 numbered minor planets with rocks."""

       import pandas as pd
       import rocks

       # Create list of identifiers for first 1000 asteroids
       N = 1000
       ids = list(range(1, N + 1))

       # Create the rocks instances
       asteroids = rocks.rocks(ids)

       # Create a dataframe containing the asteroid names, numbers,
       # their taxonomic class.
       data = [{"number": ast.number, "name": ast.name, "class_": ast.taxonomy.class_} for ast in asteroids]

       data = pd.DataFrame(data)

       # Print the distribution of taxonomic classes
       print(data.class_.value_counts())

.. _thermal_barbarians:

.. dropdown:: What is the distribution of thermal inertias of known Barbarian asteroids?

    .. code-block:: python

       #!/usr/bin/env python
       """Retrieve thermal inertias of known Barbarian asteroids."""

       import rocks

       # List of known Barbarians from Devogèle+ 2018
       BARBARIANS = [172, 234, 236, 387, 402, 458, 599, 606,
                     611, 679, 729, 824, 980, 1284, 1372, 2085]

       # Convert into list of Rock instances
       barbarians = rocks.rocks(BARBARIANS)

       thermal_ineratias = [barbarian.thermal_inertia.value for barbarian in barbarians]
       print(thermal_ineratias )

.. dropdown:: What's the weighted average albedo of (6) Hebe?

  The average albedo can be retrieved using the ``diamalbedo`` :ref:`datacloud catalogue<Datacloud Catalogue>`. The ``weighted_average()`` method of the :term:`DataCloudDataFrame` class is used to compute the average based on the best available observations of the parameter. The average is available in a ``python`` script via

  .. code-block:: python

      >>> import rocks
      >>> hebe = rocks.Rock(6, datacloud="albedos")
      >>> hebe.albedos.weighted_average("albedo")
      (0.2397586986597045, 0.009518727398082856)

.. card::
   :link: iterate_catalogues
   :link-type: ref

   **How do I access the entries in a catalogue one by one?**  :octicon:`chevron-right;1em`

Data Analysis
--------------

.. _rocksrocks:

.. dropdown:: How do I efficiently get the data of a large number of asteroids?

    The ``rocks.rocks()`` function serves as a one-line replacement for a frequent
    approach: get a list of asteroid identifiers from a catalogue and create
    ``Rock`` instances from them.

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

.. dropdown:: Can I use my own data to build a ``Rock`` object?

    You can provide a custom ssoCard to populate the ``Rock`` attributes. The ``ssocard`` argument
    accepts a ``dict``\ ionary structure following the one of the original ssoCards. The easiest way
    to achieve this is to edit a real ssoCard from SsODNet and load it via the ``json`` module.

    .. code-block:: python

        >>> import json
        >>> import os
        >>> import rocks
        >>> with open("my_ssocard.json", "r") as file_:
        >>>    data = json.load(file_)
        >>> mars_crosser_2016fj = rocks.Rock("2016_FJ", ssocard=data["2016_FJ"])


SsODNet and ``rocks``
---------------------

.. card::
   :link: ssocard-datacloud
   :link-type: ref

   **What is the difference between data from the ssoCard and from the datacloud?**  :octicon:`chevron-right;1em`

.. card::
   :link: cache-directory
   :link-type: ref

   **Is the cached asteroid data out-of-date? How do I update it?**  :octicon:`chevron-right;1em`

.. card::
   :link: parameter_aliases
   :link-type: ref

   **Which parameters can be abbreviated?**  :octicon:`chevron-right;1em`

.. card::
   :link: parameter_aliases
   :link-type: ref

   **Which parameters can I open in a plot?** :octicon:`chevron-right;1em`

.. _set_log_level:

.. dropdown:: I see too many ``WARNING``\s I don't care about. How do I change the verbosity of ``rocks``?

   The ``rocks.set_log_level(LEVEL)`` function can be used to set the verbosity of ``rocks``. The default level
   is ``INFO``, meaning that all messages with a priority of ``INFO`` or higher are printed. To see only the most relevant
   information, you can use ``rocks.set_log_level("error")``.

   See https://docs.python.org/3/library/logging.html#levels  for more information on the different levels.

.. _error_404:

.. dropdown:: I got ``Error 404: missing ssoCard for IDENTIFIER``. What is happening?

  ``rocks`` tried to retrieve the :term:`ssoCard` of a confirmed identifier and
  got an invalid response from SsODNet. This can have different reasons:

  - The confirmed identifier is outdated. This may happen if an asteroid has
    recently been named or the designation has changed. In this cases, the ssoCard is associated to
    the new name of the asteroid, while ``rocks`` may still look for it under its previous
    designation. Updating the :term:`Asteroid name-number index` via ``$ rocks status`` fixes this.

  - The :term:`ssoCard` is unavailable due to a compilation error on the SsODNet
    side. You can confirm this by looking up the ssoCard directly on SsODNet (replace ``IDENTIFIER`` in the URL below by the confirmed :term:`SsODNet ID` of the asteroid):

    http://ssp.imcce.fr/webservices/ssodnet/api/ssocard.php?q=IDENTIFIER

    If the returned ssoCard is ``null``, the card does not exist. This may be
    fixed at the next weekly recompilation of all ssoCards.
