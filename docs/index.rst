``rocks``
=========

A ``python`` package to query asteroid data from
`SsODNet <https://ssp.imcce.fr/webservices/ssodnet/>`_.

**Disclaimer: The SsODNet service and its database are in an alpha version and
under constant revision. The provided values and access methods may change
without notice.**


It includes a command-line interface for quick exploration of singular objects,

::

   $ rocks identify 221
   (221) Eos

   $ rocks taxonomy Eos
   ref                  class scheme     method  waverange
   Tholen+1989          S     Tholen     Phot    VIS        [ ]
   Bus&Binzel+2002      K     Bus        Spec    VIS        [ ]
   MotheDiniz+2005      K     Bus        Spec    VIS        [ ]
   MotheDiniz+2008a     K     Bus        Spec    VISNIR     [ ]
   Clark+2009           K     Bus-DeMeo  Spec    VISNIR     [ ]
   DeMeo+2009           K     Bus-DeMeo  Spec    VISNIR     [X]

   $ rocks albedo Eos
   ref                  albedo err   method
   Morrison+2007        0.123  0.025 STM      [ ]
   Tedesco+2001         0.140  0.010 STM      [ ]
   Ryan+2010            0.150  0.012 STM      [ ]
   Ryan+2010            0.121  0.019 NEATM    [X]
   Usui+2011            0.131  0.014 NEATM    [X]
   Masiero+2011         0.165  0.038 NEATM    [X]
   Masiero+2012         0.166  0.021 NEATM    [X]
   Masiero+2014         0.180  0.027 NEATM    [X]
   Nugent+2016          0.140  0.091 NEATM    [X]
   Nugent+2016          0.150  0.171 NEATM    [X]
   
         0.147 +- 0.004

   $ rocks info Eos | grep ProperSemimajor
          "ProperSemimajorAxis": "3.0123876",
          "err_ProperSemimajorAxis": "0.00001553",

as well as functions to retrieve properties for multiple minor bodies at once:

.. code-block:: python

   from rocks import names
   from rocks import properties

   # A collection of asteroid identifiers
   ssos = [4, 'eos', '1992EA4', 'SCHWARTZ', '1950 RW', '2001je2']

   # Resolve their names and numbers
   names_numbers = names.get_name_number(ssos)
   names = [nn[0] for nn in names_numbers]

   print(names_numbers)
   # [('Vesta', 4), ('Eos', 221), ('1992 EA4', 30863), ('Schwartz', 13820),
   #  ('Gyldenkerne', 5030), ('2001 JE2', 131353)]

   # Get their taxonomy
   taxa = properties.get_property('taxonomy', names, verbose=True, skip_quaero=True)
   classes = [t[0] for t in taxa]

   print(list(zip(names, classes)))
   # [('Vesta', 'V'), ('Eos', 'K'), ('1992 EA4', 'Ds'), ('Schwartz', 'B'),
   #  ('Gyldenkerne', False), ('2001 JE2', 'CX')]


What's been implemented so far
------------------------------

- Identify asteroids based on their number, name, or designation
  :ref:`via the command-line <cli-identify>`, or :ref:`scripted as batch job <identify>`.

- Get the taxonomic classifications of asteroids
  :ref:`via the command-line <cli-taxonomy>`, or :ref:`scripted as batch job <taxonomy>`.

- Get the albedo measurements of asteroids
  :ref:`via the command-line <cli-albedo>`, or :ref:`scripted as batch job <albedo>`.

- Get the diameter measurements of asteroids
  :ref:`via the command-line <cli-diameter>`, or :ref:`scripted as batch job <albedo>`.

- Get the mass estimates of asteroids
  :ref:`via the command-line <cli-mass>`, or :ref:`scripted as batch job <albedo>`.

- Get all data availabe on `SsODNet <https://ssp.imcce.fr/webservices/ssodnet/>`_
  for a single asteroid :ref:`via the command-line <cli-info>`.


What's to come
--------------

- Multiprocessing of batch job queries
- Retrieve all observations at the `Minor Planet Centre <https://minorplanetcenter.net/>`_
  and export them filtered by target, observation, and band
   

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   cli
   names
   properties
   tools
