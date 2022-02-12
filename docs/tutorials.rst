#########
Tutorials
#########

.. role:: raw-html(raw)
    :format: html

Asteroid Identification
=======================

- :ref:`How do I identify an asteroid from the command line?<cli_id>`

- :ref:`How do I identify an asteroid in a python script?<Identification of asteroids>`

- :ref:`How do I update the designations of many asteroids in a pandas dataframe?<update_pandas_names>`

- :ref:`Instead of a list of tuples, how can I get the list of resolved asteroid names from my identifiers? <>`

- :ref:`How can I get the aliases (e.g. outdated designations, packed designation) of this asteroid?<find_aliases>`

- :ref:`What asteroids are in the SDSS MOC1? <sdssmoc1>`

Data Exploration
================

- :ref:`How do I get asteroid parameters on the command line? <Data Exploration>`

- :ref:`How do I get all the taxonomic classes proposed for Ceres?<ceres_taxonomies>`

- :ref:`How do I get the diameters of the first 100 numbered minor planets?<first_diameters>`

- :ref:`What is the average weighted albedo of Hebe? <weighted_average_scripted>`

- :ref:`Which parameters can I open in a plot?`

- :ref:`Which parameters can be abbreviated? <Parameter Aliases>`

- :ref:`How do I access the entries in a catalogue one by one? <iterate_catalogues>`

Putting It All Together
=======================

- :ref:`What's the proper semi-major axis distribution of the Koronis family?`


Miscellaneous
==============

-  :ref:`What is the difference between data from the ssoCard and from the datacloud? <ssocard-datacloud>`

-  :ref:`Are the cached ssoCards out-of-date? How do I update ssoCards?<out-of-date>`

-  :ref:`How do I remove all cached asteroid data from my computer?<clear_cache>`

-  :ref:`I got 'Error 404: missing ssoCard'. What is happening?<error_404>`

---


.. _update_pandas_names:

*How do I update the designations of many asteroids in a pandas dataframe?*

A one-liner suffices to ensure that all designations and names are up-to-date:

.. code-block:: python

   import pandas as pd
   import rocks

   data = pd.read_csv("/path/to/data.csv")

   # Assuming that the asteroid names and designations are in a column called "name"
   data["name"] = [name for name, number in rocks.identify(data["name"])]

   # To update the numbers, just change the list comprehension
   data["number"] = [number for name, number in rocks.identify(data["name"])]

The example below achieves the same thing with a single run of `rocks.identify`, however, the code
is less comprehensible. Note that although the name resolution is asynchronous,
the order of the returned name-number tuples is guaranteed to reflect the order
of the passed identifiers.

.. code-block:: python

   data["name"], data["number"] = *zip(rocks.identify(data["name"]))

.. _sdssmoc1:

*What asteroids are in the SDSS MOC1?*

.

`SDSS MOC1 <https://faculty.washington.edu/ivezic/sdssmoc/sdssmoc1.html>`_ using ``rocks.identify``:

.. code-block:: python

    import numpy as np
    import pandas as pd
    import rocks

    # ------
    # Download SDSS MOC1 (6.2MB)
    data = pd.read_fwf(
        "https://faculty.washington.edu/ivezic/sdssmoc/ADR1.dat.gz",
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

---

.. _ceres_taxonomies:

*How do I get all the taxonomic classes proposed for Ceres?*

The taxonomic classes assigned to minor planets in public literature are available in the ``taxonomies`` :ref:`datacloud catalogues <Datacoud Catalogue>`. They can be retrieved via the command line

.. code-block:: bash

   $ rocks taxonomies Ceres

and in a ``python`` script as :ref:`DataCloudDataFrame` instance

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

---

.. _first_diameters:

*How do I get the diameters of the first 100 numbered minor planets?*

.. code-block:: python


    .. #!/usr/bin/env python

    .. """Retrieve taxonomies of first 1000 numbered minor planets with rocks.
    .. """
    .. import time

    .. import pandas as pd
    .. from rocks import rocks

    .. start = time.time()

    .. # Create list of identifiers for first 1000 asteroids
    .. N = 1000
    .. ids = list(range(1, N + 1))

    .. # Create the rocks instances
    .. asteroids = rocks(ids)

    .. # Create a dataframe containing the asteroid names, numbers,
    .. # their taxonomic class.
    .. data = [
        .. {"number": ast.number, "name": ast.name, "class_": ast.taxonomy.class_} for ast in asteroids
    .. ]

    .. data = pd.DataFrame(data)

    .. # Print the distribution of taxonomic classes
    .. print(data.class_.value_counts())

    .. print(f"This took {time.time() - start:.3} seconds.")


.. _find_aliases:

---

  *How can I get the aliases (e.g. outdated designations, packed designation) of this asteroid?*

  .

  Asteroid aliases are not stored in the :term:`ssoCard`. Instead, they are returned when querying the asteroid with `quaero <https://ssp.imcce.fr/webservices/ssodnet/api/quaero/>`_. A quick way to get the aliases of an asteroid is therefore to echo the ``link`` parameter in the asteroid's :term:`ssoCard`

  .. code-block:: bash

     $ rocks link Hebe

  and open the link which is given under the ``quaero`` key in the printed dictionary.

  .. code-block:: json

    {
    class: [
      "MB",
      "Inner"
    ],
    name: "Hebe",
    id: "Hebe",
    parent: "Sun",
    physical-models: [
      1,
      2
    ],
    aliases: [
      "00006",
      "1847 NA",
      "1947 JB",
      "2000006",
      "6",
      "I47N00A",
      "J47J00B"
    ],
    system: "Sun",
    physical-ephemeris: true,
    type: "Asteroid",
    updated: "2020-05-27",
    ephemeris: true
    }

---

.. _weighted_average_scripted:

*What's the weighted average albedo of (6) Hebe?*

.

The average albedo can be retrieved using the ``diamalbedo`` :ref:`datacloud catalogue<Datacloud Catalogue>`. The ``weighted_average()`` method of the :term:`DataCloudDataFrame` class is used to compute the average based on the best available observations of the parameter. The average is available in a ``python`` script via

.. code-block:: python

    >>> import rocks
    >>> hebe = rocks.Rock(6, datacloud="albedos")
    >>> hebe.albedos.weighted_average("albedo")
    (0.23472026283829472, 0.005766951500463558)

---

.. _error_404:

*I got 'Error 404: missing ssoCard for IDENTIFIER'. What is happening?*

``rocks`` tried to retrieve the :term:`ssoCard` of a confirmed identifier and
got an invalid response from SsODNet. This can have several reasons:

- The confirmed identifier is outdated. This may happen if an asteroid has
  recently been named. In this cases, the ssoCard is associated to the new name of the asteroid, while ``rocks`` may still look for it under its previous designation. Updating the :term:`Asteroid name-number index` via ``$ rocks status`` fixes this.

- The :term:`ssoCard` is unavailable due to a compilation error on the SsODNet
  side. You can confirm this by looking up the ssoCard directly on SsODNet (replace ``IDENTIFIER`` in the URL below by the confirmed :term:`SsODNet ID` of the asteroid):

  :raw-html:`<br />`


  http://ssp.imcce.fr/webservices/ssodnet/api/ssocard.php?q=IDENTIFIER

  :raw-html:`<br />`

  If the returned ssoCard is ``null``, the card does not exist. This may be
  fixed at the next weekly recompilation of all ssoCards.
