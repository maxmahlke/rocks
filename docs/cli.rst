.. _cli:

Command-Line Interface
======================


.. _cli-docs:

.. click:: cli:docs
  :prog: rocks docs


.. _cli-identify:

.. click:: cli:identify
  :prog: rocks identify

Asteroid names or designations are queried case- and
whitespace-insensitive.


.. _cli-index:

.. click:: cli:index
  :prog: rocks index

The index is used for local asteroid name and number lookups. It should be kep
up-to-date. If the index file is older than 30 days, a warning is displayed.

**For all functions below, providing no argument triggers a selection from the
asteroid index.**


.. _cli-taxonomy:

.. click:: cli:taxonomy
  :prog: rocks taxonomy

A taxonomic classification is highlighted based on the wavelength-range,
classification method, classification scheme, and recency of the results.
The values of each category are assigned points, and the classification
with the most points is chosen. For details, refer to the :ref:`Taxonomy
<taxonomy>`
section of the documentation.

.. _cli-albedo:

.. click:: cli:albedo
  :prog: rocks albedo

An averaged albedo value is output based on the available measurements. The
methods of albedo determination are ranked. If two measurements are
available for methods in the top ranks, these values are averaged. For
details, see the :ref:`Albedo <albedo>` section of the documentation.

.. _cli-info:

.. click:: cli:info
  :prog: rocks info

