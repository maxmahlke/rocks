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
asteroid in the requested catalogue.

When querying for asteroid parameters, specifying the parameter name as singular or plural will retrieve its
value from the ``ssoCard`` in the former and from the ``datacloud`` in the latter case, as shown below.

.. code-block:: bash

   $ rocks taxonomy Eos
   K

   $ rocks taxonomies Eos
   +-----------+---------+--------+-----------+------------------+------+--------+
   | scheme    | complex | method | waverange | shortbib         | year | class_ |
   +-----------+---------+--------+-----------+------------------+------+--------+
   | Tholen    | S       | Phot   | VIS       | Tholen+1989      | 1989 | S      |
   | Bus       | K       | Spec   | VIS       | Bus&Binzel+2002  | 2002 | K      |
   | Bus       | K       | Spec   | VIS       | MotheDiniz+2005  | 2005 | K      |
   | Bus       | K       | Spec   | VISNIR    | MotheDiniz+2008a | 2008 | K      |
   | Bus-DeMeo | K       | Spec   | VISNIR    | Clark+2009       | 2009 | K      |
   | Bus-DeMeo | K       | Spec   | VISNIR    | DeMeo+2009       | 2009 | K      |
   +-----------+---------+--------+-----------+------------------+------+--------+

.. code-block:: python

   >>> from rocks import Rock
   >>> ceres = Rock(1, datacloud='taxonomies')
   >>> ceres.taxonomy.class_    # ssoCard
   'C'
   >>> ceres.taxonomies.class_  # datacloud
   ['G', 'C', 'C', 'C', 'C', 'G', 'C']


``ssoCards`` and ``datacloud`` catalogues are :ref:`cached on your computer <cache-directory>` for quicker data access.

.. _out-of-date:

Updating the Cached Data
=================================

All ``ssoCards`` and ``datacloud`` catalogues are updated and recompiled weekly
by :term:`SsODNet`. It is therefore recommended to either remove or update the
cached data regularly. The ``$ rocks status`` command offers to do just this.

.. code-block:: bash

   $ rocks status

    Contents of /home/mmahlke/.cache/rocks:

            48179 ssoCards
            3598 datacloud catalogues

            Asteroid name-number index [index.pkl] updated on 08 Dec 2021
            Metadata files ['ssoCard_description.json', 'ssoCard_units.json']

    Update or clear the cached ssoCards and datacloud catalogues?
    [0] Do nothing [1] Clear the cache [2] Update the data (1): 1

    Update the asteroid name-number index?
    [0] No [1] Yes (1): 0
