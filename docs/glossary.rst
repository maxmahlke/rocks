########
Glossary
########

.. glossary::

  Asteroid name-number index

    The index of the currently numbered asteroids including their numbers, names or designations, and :term:`SsODNet IDs<SsODNet ID>`. It is stored as ``index.pkl`` in the :term:`cache directory <Cache Directory>` and can be updated with ``$ rocks update``.

  Cache Directory

   Storage location for the retrieved ssoCards and datacloud catalogues, as well as the asteroid name-number index and ssoCard metadata files. Located in the user's home directory as ``~/.cache/rocks``.

  Datacloud Catalogue

   The `datacloud <https://ssp.imcce.fr/webservices/ssodnet/api/datacloud/>`_ is
   an aggregation of publicly available data of minor planets. The catalogues it
   provides contain e.g. asteroid diameters and albedos (``diamalbedo``),
   asteroid proper elements (``astdys``), or measurements of the Yarkovsky
   effect (``yarkovskies``). Each catalogue contains data on many asteroids and
   each asteroid can appear multiple times in the catalogue. They are retrieved
   and stored as ``JSON`` files in the :term:`cache directory<Cache Directory>`.

  DataCloudDataFrame

   The ``python`` implementation of a :term:`datacloud catalogue <Datacloud
   Catalogue>` is the ``DataCloudDataFrame`` class. As the name suggests, it is
   a subclass of the ``pandas``  ``DataFrame`` and inherits its properties. The
   only  difference to the ``DataFrame`` is the overloaded ``plot()`` method
   and the added ``weighted_average()`` method. by the abbreviation on the
   right.

  Identifier

    A user-provided string, float, or integer, which serves to identify an
    asteroid. It can refer to the asteroid's name (``"Eos"``), the number
    (``221``), previous or current designations (``"1882 BA"``), packed designations (``"I82B00A"``) and other aliases as defined by `quaero
    <https://ssp.imcce.fr/webservices/ssodnet/api/quaero/>`_. The identifier is
    *not* case-sensitive and frequent shortforms (such as dropping the
    whitespace in the designation, ``"1882BA"``) are accepted as well.

  ssoCard

   The `ssoCard <https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/>`_
   represents the best available measurements (or a product thereof) of the
   parameters of a single asteroid. Each asteroid has a single ssoCard and each
   ssoCard refers to a single asteroid. They are retrieved and stored as
   ``JSON`` files in the :term:`cache directory<Cache Directory>`.


  SsODNet

    The *Virtual Observatory Solar system Open Database Network* `SsODNet <https://ssp.imcce.fr/webservices/ssodnet/>`_ is a name resolver and data aggregator for minor planets.

  SsODNet ID

   The `identifier <https://ssp.imcce.fr/webservices/ssodnet/api/resolver/#output-params>`_ used by the SsODNet database to refer to this specific asteroid. For ``(1) Ceres``, it's ``Ceres``. For ``2021 JB32``, it's ``2021_JB32``. Queries for asteroid name resolution or data are faster when providing this identifier right away.
