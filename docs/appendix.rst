########
Appendix
########

.. _parameter_names:

ssoCard Parameter Attribute Names
---------------------------------

The :term:`ssoCard<ssoCard>` parameters are available under the attribute
names given below. Deviations from the original names mostly derive from the concept
that ssoCard parameters are accessed via singular-case attribute names while the corresponding
:term:`datacloud catalogues<Datacloud Catalogue>` are available under the plural-case version.

+---------------------------------------------+-----------------------------------------------+
| SsODNet Catalogue                           |  Attribute Name                               |
+---------------------------------------------+-----------------------------------------------+
| id                                          |  ``id_``                                      |
+---------------------------------------------+-----------------------------------------------+
| name                                        |  ``name``                                     |
+---------------------------------------------+-----------------------------------------------+
| type                                        |  ``type``                                     |
+---------------------------------------------+-----------------------------------------------+
| class                                       |  ``class_``                                   |
+---------------------------------------------+-----------------------------------------------+
| number                                      |  ``number``                                   |
+---------------------------------------------+-----------------------------------------------+
| parent                                      |  ``parent``                                   |
+---------------------------------------------+-----------------------------------------------+
| system                                      |  ``system``                                   |
+---------------------------------------------+-----------------------------------------------+
|                                             |                                               |
+---------------------------------------------+-----------------------------------------------+
| parameters.physical.absolute_magnitude      |  ``absolute_magnitude``                       |
+---------------------------------------------+-----------------------------------------------+
| parameters.physical.albedo                  |  ``albedo``                                   |
+---------------------------------------------+-----------------------------------------------+
| parameters.physical.colors                  |  ``color``                                    |
+---------------------------------------------+-----------------------------------------------+
| parameters.physical.density                 |  ``density``                                  |
+---------------------------------------------+-----------------------------------------------+
| parameters.physical.diameter                |  ``diameter``                                 |
+---------------------------------------------+-----------------------------------------------+
| parameters.physical.mass                    |  ``mass``                                     |
+---------------------------------------------+-----------------------------------------------+
| parameters.physical.phase_functions         |  ``phase_function``                           |
+---------------------------------------------+-----------------------------------------------+
| parameters.physical.spins                   |  ``spin``                                     |
+---------------------------------------------+-----------------------------------------------+
| parameters.physical.taxonomy                |  ``taxonomy``                                 |
+---------------------------------------------+-----------------------------------------------+
| parameters.physical.thermal_inertia         |  ``thermal_inertia``                          |
+---------------------------------------------+-----------------------------------------------+
|                                             |                                               |
+---------------------------------------------+-----------------------------------------------+
| parameters.dynamical.orbital_elements       |  ``orbital_elements``                         |
+---------------------------------------------+-----------------------------------------------+
| parameters.dynamical.proper_elements        |  ``proper_elements``                          |
+---------------------------------------------+-----------------------------------------------+
| parameters.dynamical.pairs                  |  ``pair``                                     |
+---------------------------------------------+-----------------------------------------------+
| parameters.dynamical.delta_v                |  ``delta_v``                                  |
+---------------------------------------------+-----------------------------------------------+
| parameters.dynamical.delta_v.2burns         |  ``delta_v.two_burns``                        |
+---------------------------------------------+-----------------------------------------------+
| parameters.dynamical.delta_v.tt_3burns      |  ``delta_v.tt_three_burns``                   |
+---------------------------------------------+-----------------------------------------------+
| parameters.dynamical.delta_v.3burns         |  ``delta_v.three_burns``                      |
+---------------------------------------------+-----------------------------------------------+
| parameters.dynamical.delta_v.tt_2burns      |  ``delta_v.tt_two_burns``                     |
+---------------------------------------------+-----------------------------------------------+
| parameters.dynamical.tisserand_parameter    |  ``tisserand_parameter``                      |
+---------------------------------------------+-----------------------------------------------+
| parameters.dynamical.moid                   |  ``moid``                                     |
+---------------------------------------------+-----------------------------------------------+
| parameters.dynamical.source_regions         |  ``source_regions``                           |
+---------------------------------------------+-----------------------------------------------+
| parameters.dynamical.yarkovsky              |  ``yarkovsky``                                |
+---------------------------------------------+-----------------------------------------------+
|                                             |                                               |
+---------------------------------------------+-----------------------------------------------+
| parameters.eq_state_vector.position         |  ``position``                                 |
+---------------------------------------------+-----------------------------------------------+
| parameters.eq_state_vector.ref_epoch        |  ``ref_epoch``                                |
+---------------------------------------------+-----------------------------------------------+
| parameters.eq_state_vector.velocity         |  ``velocity``                                 |
+---------------------------------------------+-----------------------------------------------+

.. _bibref_spins_access:

Note that while ``spins`` in the :term:`ssoCard` are stored in a dictionary, they are stored
as a list in the ``spin`` attribute of the ``Rock`` class. As for :ref:`bibref<bibman>` lists,
the joint attributes of the different spin solutions can be accessed via the dot notation.
Selecting a specific solution via its index from the ``spin`` list returns only the corresponding
value.

.. code-block:: python

   >>> import rocks
   >>> rocks.Rock(3801)
   Rock(number=3801, name='Thrasymedes')
   >>> rocks.Rock(3801).spin.period
   [
     FloatValue(error=Error(min_=-0.349972, max_=0.349972), value=20.235073, error_=0.349972),
     FloatValue(error=Error(min_=-0.06, max_=0.06), value=9.6, error_=0.06),
     FloatValue(error=Error(min_=-1.0, max_=1.0), value=16.02, error_=1.0)
   ]
   >>> rocks.Rock(3801).spin.period.value
   [20.235073, 9.6, 16.02]
   >>> rocks.Rock(3801).spin[0].period.value
   20.235073
   >>> rocks.Rock(3801).spin[1].period.value
   9.6



.. _catalogue_names:

Datacloud Catalogue Attribute Names
-----------------------------------

The :term:`datacloud catalogues<Datacloud Catalogue>` are available under the attribute
names given below. Note that the plural of ``proper_elements`` is defined as ``proper_elements_``
due to a lack of more convincing alternatives.

+---------------------------+-----------------------------------------------+
| SsODNet Catalogue         |  Attribute Name                               |
+---------------------------+-----------------------------------------------+
| Astorb                    |  ``astorb``                                   |
+---------------------------+-----------------------------------------------+
| Binarymp                  |  ``binarymp``                                 |
+---------------------------+-----------------------------------------------+
| Colors                    |  ``colors``                                   |
+---------------------------+-----------------------------------------------+
| Density                   |  ``densities``                                |
+---------------------------+-----------------------------------------------+
| Diamalbedo                |  ``diamalbedo`` / ``diameters`` / ``albedos`` |
+---------------------------+-----------------------------------------------+
| Families                  |  ``families``                                 |
+---------------------------+-----------------------------------------------+
| Masses                    |  ``masses``                                   |
+---------------------------+-----------------------------------------------+
| Mpcatobs                  |  ``mpcatobs``                                 |
+---------------------------+-----------------------------------------------+
| Pairs                     |  ``pairs``                                    |
+---------------------------+-----------------------------------------------+
| Proper Elements           |  ``proper_elements_``                         |
+---------------------------+-----------------------------------------------+
| Phase Functions           |  ``phase_functions``                          |
+---------------------------+-----------------------------------------------+
| Taxonomies                |  ``taxonomies``                               |
+---------------------------+-----------------------------------------------+
| Thermal Inertias          |  ``thermal_inertias``                         |
+---------------------------+-----------------------------------------------+
| Shapes                    |  ``shapes``                                   |
+---------------------------+-----------------------------------------------+
| Spins                     |  ``spins``                                    |
+---------------------------+-----------------------------------------------+
| Yarkovsky                 |  ``yarkovskys``\ [#f1]_                       |
+---------------------------+-----------------------------------------------+

Within the catalogues, columns referring to numbers are renamed for consistency.

+-----------------+-----------------------------+
| datacloud Table | Attribute Name in ``rocks`` |
+-----------------+-----------------------------+
| num             | ``number``                  |
+-----------------+-----------------------------+
| sibling_num     | ``sibling_number``          |
+-----------------+-----------------------------+

.. _parameter_aliases:

Parameter Aliases
-----------------

Some parameters in the ssoCard have commonly used aliases defined to avoid verbosity. Both on the
command-line and in the ``python`` interface, you can replace the parameter name given on the left
by the abbreviation on the right. Feel free to suggest a new alias via the `GitHub issues page
<https://github.com/maxmahlke/rocks/issues>`_.

+---------------------------+------------------------+
| Parameter Name in ssoCard |  Alias Name            |
+---------------------------+------------------------+
| semi_major_axis           |  a                     |
+---------------------------+------------------------+
| eccentricity              |  e                     |
+---------------------------+------------------------+
| inclination               |  i                     |
+---------------------------+------------------------+
| proper_semi_major_axis    |  ap                    |
+---------------------------+------------------------+
| proper_eccentricity       |  ep                    |
+---------------------------+------------------------+
| proper_inclination        |  ip                    |
+---------------------------+------------------------+
| proper_sine_inclination   |  sinip                 |
+---------------------------+------------------------+
| orbital_period            |  P                     |
+---------------------------+------------------------+
| absolute_magnitude        |  H                     |
+---------------------------+------------------------+
| generic_johnson_V         |  V                     |
+---------------------------+------------------------+
| misc_atlas_cyan           |  cyan                  |
+---------------------------+------------------------+
| misc_atlas_orange         |  orange                |
+---------------------------+------------------------+

.. _need_suffix:

The following parameters need an ``_``-suffix when accessing them using the ``python`` interface:

.. code-block:: python

   ['class', 'from', 'id', 'lambda', 'long', 'max', 'min', 'type']

.. _lite_columns:

BFT Columns
-----------

The list of columns loaded by default from the BFT:

.. code-block:: python

  COLUMNS = [
      "sso_id",
      "sso_number",
      "sso_name",
      "sso_class",
      "orbital_elements.semi_major_axis.value",
      "orbital_elements.eccentricity.value",
      "orbital_elements.inclination.value",
      "orbital_elements.orbital_period.value",
      "orbital_elements.periapsis_distance.value",
      "proper_elements.proper_semi_major_axis.value",
      "proper_elements.proper_eccentricity.value",
      "proper_elements.proper_inclination.value",
      "proper_elements.proper_sine_inclination.value",
      "family.family_number",
      "family.family_name",
      "pair.sibling_number",
      "pair.sibling_name",
      "pair.distance",
      "pair.age.value",
      "yarkovsky.dadt.value",
      "yarkovsky.A2.value",
      "yarkovsky.S",
      "albedo.value",
      "absolute_magnitude.value",
      "density.value",
      "diameter.value",
      "mass.value",
      "taxonomy.class",
      "taxonomy.complex",
      "taxonomy.waverange",
      "taxonomy.technique",
      "thermal_inertia.value",
      "spins.1.period.value",
  ]

.. rubric:: Footnotes

.. [#f1] I agree, it looks terrible.
