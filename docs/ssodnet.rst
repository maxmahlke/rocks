##############
Available Data
##############

``rocks`` provides easy access to the asteroid data stored on `SsODNet <https://ssp.imcce.fr/webservices/ssodnet/>`_.
There are two main data repositories, the `ssoCard <https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/>`_
and the `datacloud <https://ssp.imcce.fr/webservices/ssodnet/api/datacloud/>`_.

.. _ssocard-datacloud:

ssoCard and datacloud
=====================

Every known asteroid has an ``ssoCard`` and every ``ssoCard`` only refers to a
single asteroid. It stores the best single value for each parameter
of the asteroid, e.g. by computing weighted averages of the best available data.

The ``datacloud`` is the collection of (almost) all published data on asteroids.
It is split into catalogues, e.g. the ``diamalbedo`` catalogue containing
observations of asteroid diameters and albedos. ``rocks`` offers to query these
catalogues for one asteroid at a time, returning all entries belonging to that
asteroid in that catalogue.

In `rocks`, the parameter names are singular if they refer to the value in the
``ssoCard`` and plural if they refer to the ``datacloud`` entries. When creating
a `rocks.Rock` instance, ``datacloud`` catalogues which should be available have
to be specified explicitly (to avoid unnecessary data queries and retrievals).

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

After some weeks / months, the data in the cached ssoCards may be outdated. The
``$ rocks update`` command echos the number of locally cached ssoCards  and
checks their version against the current SsODNet global ssoCard version. If any
ssoCard is out-of-date, ``rocks`` offers to retrieve the latest versions of
these cards.

.. code-block:: bash

   $ rocks update

.. _still-out-of-date:

If ``$ rocks update`` still lists outdated cards on a second run, they may belong to asteroids which have been named recently. These cards can be deleted.

.. _clear_cache:

Removing the cached asteroid data
---------------------------------

You can delete all cached ssoCards and datacloud catalogues by running

.. code-block:: bash

   $ rocks clear
