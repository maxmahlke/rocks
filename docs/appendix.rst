########
Appendix
########

.. _parameter_names:

TBD

.. _catalogue_names:

Datacloud Catalogue Attribute Names
-----------------------------------

The ``diamalbedo`` catalogue is aliased to ``diameters`` and ``albedos``.

.. _parameter_aliases:

Parameter Aliases
-----------------

Some parameters in the ssoCard have commonly used aliases defined to avoid verbosity. Both
on the command-line and in the ``python`` interface, you can replace the parameter name given on the left
by the abbreviation on the right. Feel free to suggest a new alias via the `GitHub issues page <https://github.com/maxmahlke/rocks/issues>`_.

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

   ['min', 'max', 'class', 'lambda']



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

Some attributes are called different in ``rocks`` than in the ``datacloud`` table:


The ``datacloud`` tables have slightly different names in ``rocks``.

+-----------------+----------------------------+
| datacloud Table | Attribute Name             |
+-----------------+----------------------------+
| num             | ``number``                 |
+-----------------+----------------------------+
| sibling_num     | ``sibling_number``         |
+-----------------+----------------------------+
| id              | ``id_``                    |
+-----------------+----------------------------+
| lambda          | ``lambda_``                |
+-----------------+----------------------------+
| class           | ``class_``                 |
+-----------------+----------------------------+
| from           | ``from_``                   |
+-----------------+----------------------------+
