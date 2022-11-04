##############
Available Data
##############

``rocks`` provides easy access to the asteroid data stored on `SsODNet <https://ssp.imcce.fr/webservices/ssodnet/>`_.
There are two main data repositories, the `ssoCard <https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/>`_
and the `datacloud <https://ssp.imcce.fr/webservices/ssodnet/api/datacloud/>`_.

.. _ssocard-datacloud:

ssoCard and datacloud
=====================

Every known asteroid has an :term:`ssoCard` and every :term:`ssoCard` only refers to a
single asteroid. It stores the best single value for each parameter
of the asteroid, e.g. by computing weighted averages of the best available data.

The :term:`datacloud<Datacloud Catalogue>` is the collection of (almost) all
published data on asteroids. It is split into catalogues, e.g. the
``diamalbedo`` catalogue containing observations of asteroid diameters and
albedos. ``rocks`` allows to query these catalogues for one asteroid at a time,
returning all entries belonging to that asteroid in the requested catalogue.

When querying for asteroid parameters, specifying the parameter name as
singular or plural will retrieve its value from the :term:`ssoCard` in the
former and from the :term:`datacloud<Datacloud Catalogue>` in the latter case,
as shown below. See the list of available parameters :ref:`here <parameter_names>`.

.. tab-set::

  .. tab-item:: Command Line

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

  .. tab-item:: python

        .. code-block:: python

           >>> from rocks import Rock
           >>> ceres = Rock(1, datacloud='taxonomies')
           >>> ceres.taxonomy.class_    # ssoCard
           'C'
           >>> ceres.taxonomies.class_  # datacloud
           ['G', 'C', 'C', 'C', 'C', 'G', 'C']

:term:`ssoCards <ssoCard>` and :term:`datacloud <Datacloud Catalogue>`
catalogues are cached on your computer for quicker data access, as further
outlined below.

.. _cache-directory:

Data stored on your machine
===========================

``rocks`` retrieves all requested asteroid data from :term:`SsODNet` and stores
it in a :term:`cache directory<Cache Directory>` to increase following data
look-ups. The cache is located at ``~/.cache/rocks``. It is created if it does
not exist when ``rocks`` is invoked.


To reduce the time of resolving the identity of asteroids
:term:`identifiers<Identifier>`, ``rocks`` keeps a local index of asteroid
names and numbers in the :term:`cache directory<Cache Directory>`. This index is retrieved from
:term:`SsODNet` if it does not exist when ``rocks`` is invoked.

The data in the :term:`cache directory<Cache Directory>` can be updated or removed using the ``status`` command. **It should be run
regularly** (e.g. once a month) to ensure that the data is up-to-date:


.. code-block:: bash

   $ rocks status

   Contents of /home/mmahlke/.cache/rocks:

           41 ssoCards
           15 datacloud catalogues

           Asteroid name-number index updated on 12 Jul 2022

   Update or clear the cached ssoCards and datacloud catalogues?
   [0] Do nothing [1] Clear the cache [2] Update the data (1): 1

   Clearing the cached ssoCards and datacloud catalogues..

   Update the asteroid name-number index?
   [0] No [1] Yes (1): 1

   Building index |---------------------------| 100%

The command accepts two flags to skip the interactive prompts: the ``--clear`` or ``-c`` flag deletes
the cached asteroid data but leaves the index in place. The ``--update`` or ``-u`` flag updates the cached
asteroid data and updates the :term:`asteroid name-number index <Asteroid name-number index>`.
