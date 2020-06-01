Asteroid Properties
===================

.. currentmodule:: properties

The SsODNet:datacloud contains a vast collection of asteroid properties. In
general, the properties have been observed several time (e.g. the albedo). The
datacloud returns all values, while ``rocks`` contains aggregation or selection
functions to select a sensible, single value.


Implemented so far are merging schemes for 

- Albedo
- Taxonomy


.. autofunction:: get_property

Each property contains an aggregation or selection function to provide a single
return value in case of many available. This choice is a subjective
implementation, e.g. by evaluating the different taxonomic classification
methods and picking the most likely one **in the opinion of the repository
maintainers**.


.. code-block:: python

  from rocks import names
  from rocks import properties
  
  # A collection of asteroid identifiers with various degrees of abstraction
  ssos = [4, 'eos', '1992EA4', 'SCHWARTZ', '1950 RW', '2001je2']
  
  # Resolve their names and numbers
  names_numbers = names.get_name_number(ssos)
  
  print(names_numbers)
  # [('Vesta', 4), ('Eos', 221), ('1992 EA4', 30863),
  #  ('Schwartz', 13820), ('Gyldenkerne', 5030), ('2001 JE2', 131353)]

  names = [nn[0] for nn in names_numbers]
  
  # Get their taxonomy
  taxa = properties.get_property('taxonomy', names, verbose=True,
                             skip_quaero=True)
  classes = [t[0] for t in taxa]
  print(list(zip(names, classes)))
  # [('Vesta', 'V'), ('Eos', 'K'), ('1992 EA4', 'Ds'),
  #  ('Schwartz', 'B'), ('Gyldenkerne', False), ('2001 JE2', 'CX')]
  
  # Get albedos
  albedos = properties.get_property('albedo', names, verbose=True,
                                    skip_quaero=True)
  albs = [a[0] for a in albedos] # returns weighted average and uncertainty
  print(list(zip(names, albs)))
  # [('Vesta', (0.34, 0.02)), ('Eos', (0.147, 0.004)), ('1992 EA4', False),
  #  ('Schwartz', (0.051, 0.004)), ('Gyldenkerne', (0.120, 0.007)), ('2001 JE2', False)]



.. _albedo:

.. autofunction:: select_albedo

.. _diameter:

.. autofunction:: select_diameter

.. _mass:

.. autofunction:: select_mass

.. _taxonomy:

.. autofunction:: select_taxonomy
