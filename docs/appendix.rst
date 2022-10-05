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

.. _catalogue_names:

Datacloud Catalogue Attribute Names
-----------------------------------

The :term:`datacloud catalogues<Datacloud Catalogue>` are available under the attribute
names given below.

+---------------------------+-----------------------------------------------+
| SsODNet Catalogue         |  Attribute Name                               |
+---------------------------+-----------------------------------------------+
| Astorb                    |  ``astorb``                                   |
+--------------------------------------------------+------------------------+
| Binarymp                  |  ``binarymp``                                 |
+--------------------------------------------------+------------------------+
| Colors                    |  ``colors``                                   |
+---------------------------+-----------------------------------------------+
| Density                   |  ``densities``                                |
+---------------------------+-----------------------------------------------+
| Diamalbedo                |  ``diamalbedo`` / ``diameters`` / ``albedos`` |
+--------------------------------------------------+------------------------+
| Families                  |  ``families``                                 |
+--------------------------------------------------+------------------------+
| Masses                    |  ``masses``                                   |
+---------------------------+-----------------------------------------------+
| Mpcatobs                  |  ``mpcatobs``                                 |
+---------------------------+-----------------------------------------------+
| Pairs                     |  ``pairs``                                    |
+---------------------------+-----------------------------------------------+
| Proper Elements           |  ``proper_elements``                          |
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
| Yarkovskys                |  ``yarkovskys``                               |
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

.. _need_suffix:

The following parameters need an ``_``-suffix when accessing them using the ``python`` interface:

.. code-block:: python

   ['class', 'from', 'id', 'lambda', 'max', 'min']
