#########
Tutorials
#########

General FAQ
===========

-  :ref:`What is the difference between data from the ssoCard and from the datacloud? <ssocard-datacloud>`

The Data Cache
==============

-  :ref:`Are the cached ssoCards out-of-date? How do I update ssoCards?<out-of-date>`

-  :ref:`How do I remove all cached asteroid data from my computer?<clear_cache>`

Asteroid Identification
=======================

Identification - command line

Which asteroid is this?

What are the aliases (outdated designations) of this asteroid?

Identification - scripted

What are all these asteroids in the SDSS MOC4?

Property exploration - command line

What taxonomic classes have been assigned to Hygiea

What's the weighted average albedo of Ceres?

Property exploration - scripted

What's the proper semi-major axis distribution of the Koronis family?


Datacloud Catalogues
====================

- :ref:`Is there a convenient way to get the entries of a catalogue one by one? <iterate_catalogues>`


.. _weighted_average_scripted:

What's the weighted average albedo of (6) Hebe?
-----------------------------------------------

.. code-block:: python

    >>> alb_diam, err_alb_diam = rocks.utils.weighted_average(np.array(self.diameter)[self.preferred_diameter], np.array(self.err_diameter)[self.preferred_diameter])


Identify asteroids
------------------

.. highlight:: python

- Identify asteroids using a list of names, numbers, or designations::

    import rocks

    names_numbers = rocks.identify(MY_LIST_OF_IDENTIFIERS)

    NAMES = [name_number[0] for name_number in names_numbers]
    NUMBERS = [name_number[1] for name_number in names_numbers]

- Identify objects in the `SDSS MOC1 <https://faculty.washington.edu/ivezic/sdssmoc/sdssmoc1.html>`_ using ``rocks.identify``:

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

Download the file or run in a binder.

.. .. code-block:: python

    
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


.. - Using the ``Rock`` class for asteroid parameter access
.. - Plotting asteroid albedo distributions for C-types


.. ``Rock`` class for accessing asteroid parameters
.. ------------------------------------------------
.. jupyter notebooks with binder

.. identify function

.. - :ref:`resolve asteroid names from various identification formats<Asteroid name resolution>`
.. - :ref:`explore available asteroid data via the command line<Exploration via the command line>`
.. - :ref:`retrieve and compare measurements in a script<Retrieve and compare asteroid data in a script>`
.. - :ref:`retrieve parameters for thousands of asteroids in a batch-job<Retrieve parameters for a large number of asteroids>`

.. Asteroid name resolution
.. """"""""""""""""""""""""
.. ``rocks`` can identify asteroids based on a variety of identifying strings or
.. numbers.

.. .. code-block:: python

   .. from rocks import names
   .. from rocks import properties

   .. # A collection of asteroid identifiers
   .. ssos = [4, 'eos', '1992EA4', 'SCHWARTZ', '1950 RW', '2001je2']

   .. # Resolve their names and numbers
   .. names_numbers = names.get_name_number(ssos)
   .. names = [nn[0] for nn in names_numbers]

   .. print(names_numbers)
   .. # [('Vesta', 4), ('Eos', 221), ('1992 EA4', 30863), ('Schwartz', 13820),
   .. #  ('Gyldenkerne', 5030), ('2001 JE2', 131353)]

.. The name resolution algorithm and different use cases are :ref:`documented here<Resolving names, numbers, designations>`.


.. Exploration via the command line
.. """"""""""""""""""""""""""""""""
.. The ``rocks`` executable is installed system-wide upon installation of the
.. package. It has a set of subcommands.

.. .. code-block:: bash

  .. $ rocks
  .. Usage: rocks [OPTIONS] COMMAND [ARGS]...

  .. CLI for minor body exploration.

  .. For more information: rocks docs

  .. Options:
    .. --help  Show this message and exit.

  .. Commands:
    .. docs        Open rocks documentation in browser.
    .. identify    Get asteroid name and number from string input.
    .. index       Create or update index of numbered SSOs.
    .. info        Print available data on asteroid.
    .. properties  Print valid property names.

  .. $ rocks identify 221
  .. (221) Eos

   .. $ rocks info Eos | grep ProperSemimajor
          .. "ProperSemimajorAxis": "3.0123876",
          .. "err_ProperSemimajorAxis": "0.00001553",

.. When the subcommand is not recognized, ``rocks`` assumes that an asteroid
.. property is requested.  The valid property names can be printed with ``rocks properties``.

.. An asteroid identifier can be passes as second argument. Otherwise, an
.. interactive selection from an asteroid index is started.

.. .. code-block:: bash

   .. $ rocks taxonomy Eos
   .. ref                  class scheme     method  waverange
   .. Tholen+1989          S     Tholen     Phot    VIS        [ ]
   .. Bus&Binzel+2002      K     Bus        Spec    VIS        [ ]
   .. MotheDiniz+2005      K     Bus        Spec    VIS        [ ]
   .. MotheDiniz+2008a     K     Bus        Spec    VISNIR     [ ]
   .. Clark+2009           K     Bus-DeMeo  Spec    VISNIR     [ ]
   .. DeMeo+2009           K     Bus-DeMeo  Spec    VISNIR     [X]

   .. $ rocks albedo Eos
   .. ref                  albedo err   method
   .. Morrison+2007        0.123  0.025 STM      [ ]
   .. Tedesco+2001         0.140  0.010 STM      [ ]
   .. Ryan+2010            0.150  0.012 STM      [ ]
   .. Ryan+2010            0.121  0.019 NEATM    [X]
   .. Usui+2011            0.131  0.014 NEATM    [X]
   .. Masiero+2011         0.165  0.038 NEATM    [X]
   .. Masiero+2012         0.166  0.021 NEATM    [X]
   .. Masiero+2014         0.180  0.027 NEATM    [X]
   .. Nugent+2016          0.140  0.091 NEATM    [X]
   .. Nugent+2016          0.150  0.171 NEATM    [X]
   
         .. 0.147 +- 0.004


.. See ``rocks --help`` and :ref:`the documentation<Command-Line Interface>` for the implemented functions.

.. Retrieve and compare asteroid data in a script
.. """"""""""""""""""""""""""""""""""""""""""""""
.. At the core of the ``rocks`` package is the ``Rock`` class. A ``Rock`` instance represents an asteroid. Its properties are accessible via its attributes.

.. .. code-block:: python

  .. from rocks.core import Rock

  .. Ceres = Rock(1)
  .. print(Ceres)
  .. # Rock(number=1, name='Ceres')

  .. Vesta = Rock('vesta')
  .. print(Vesta)
  .. # Rock(number=4, name='Vesta') 

  .. print(Ceres.taxonomy)  # singular form: from ssoCard
  .. # 'C'
  .. print(Ceres.taxonomies)  # plurar form: all datacloud entries
  .. # ['G', 'C', 'C', 'C', 'C', 'G', 'C']

  .. print(Vesta.albedo)
  .. # 0.3447431141599281

  .. print(Vesta.albedo > Ceres.albedo)
  .. # True

.. The properties metadata and uncertainties are again attributes of the property
.. itself.

.. .. code-block:: python

  .. print(Ceres.taxonomies)
  .. # ['G', 'C', 'C', 'C', 'C', 'G', 'C']
  .. print(Ceres.taxonomies.shortbib)
  .. # ['Tholen+1989', 'Bus&Binzel+2002', 'Lazzaro+2004', 'Lazzaro+2004', 'DeMeo+2009', 'Fornasier+2014', 'Fornasier+2014']
  .. print(Ceres.taxonomies.method)
  .. # ['Phot', 'Spec', 'Spec', 'Spec', 'Spec', 'Spec', 'Spec']

.. See the ``Rock`` :ref:`class documentation<rock_class>` for details.

.. Retrieve parameters for a large number of asteroids
.. """""""""""""""""""""""""""""""""""""""""""""""""""

.. It is possible to create many ``Rock`` instances in parallel by passing a list
.. of asteroid identifiers. Selecting a subset of the property-space saves memory
.. and computation time.

.. .. code-block:: python

   .. import numpy as np
   .. from rocks.core import many_rocks

   .. # List of asteroid identifiers
   .. ssos = range(1, 1000)

   .. # Get their taxonomies and albedos in 4 parallel jobs, display progress bar
   .. rocks = many_rocks(ssos, ['taxonomy', 'albedo'], parallel=4, progress=True)

   .. # many_rocks returns a list of Rock-instances
   .. print(rocks[0])
   .. # Rock(number=1, name='Ceres')

   .. # Get the asteroid with the largest albedo

