ssoCard and datacloud
=====================

``rocks`` provides easy access to the asteroid data stored on `SsODNet <https://ssp.imcce.fr/webservices/ssodnet/>`_.
There are two main data repositories, the `ssoCard <https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/>`_
and the `datacloud <https://ssp.imcce.fr/webservices/ssodnet/api/datacloud/>`_.

Every known asteroid has an `ssoCard` and every `ssoCard` only refers to a
single asteroid. It is meant to store the best single value for each parameter
of the asteroid. Example: If an asteroid has been taxonomically classified in 10
different publications but only one of them used a complete
visible-near-infrared spectrum for the classification, only the assigned
taxonomic class from that work will appear in the `ssoCard`.

The `datacloud` is the collection of (almost) all published data on asteroids. It is split into catalogues, for example the `diamalbedo` catalogue containing observations of asteroid diameters and albedos. ``rocks`` offers to query these catalogues for one asteroid at a time, returning all entries belonging to that asteroid in that catalogue.

In `rocks`, the parameter names are singular if they refer to the value in the `ssoCard` and plural if they refer to the `datacloud` entries. When creating a `rocks.Rock` instance, `datacloud` catalogues which should be available have to be specified explicitly (to avoid unnecessary data queries and retrievals).

.. code-block:: bash

   $ rocks taxonomy.class_ Ceres    # ssoCard
   C

   $ rocks taxonomies.class_ Ceres  # datacloud
   ['G', 'C', 'C', 'C', 'C', 'G', 'C']

.. code-block:: python

   >>> from rocks import Rock
   >>> ceres = Rock(1, datacloud='taxonomies')
   >>> ceres.taxonomy.class_    # ssoCard
   'C'
   >>> ceres.taxonomies.class_  # datacloud
   ['G', 'C', 'C', 'C', 'C', 'G', 'C']


:ref:`ssoCards and datacloud catalogues are cached on your computer for quicker data access.<cache-directory>`

.. _out-of-date:

Updating the cached asteroid data
---------------------------------

After some weeks / months, the data in the cached ssoCards may be outdated. The ``$ rocks status`` command echos the number of locally cached ssoCards and checks their version against the current SsODNet global ssoCard version. If any ssoCard is out-of-date, ``rocks`` offers to retrieve the latest versions of these cards.

.. code-block:: bash

   $ rocks status

You can delete all cached ssoCards by running

.. code-block:: bash

   $ rocks clear
