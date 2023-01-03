#############
Giving Credit
#############

If you made use of ``rocks`` for your publication, you might want to credit (1)
the original authors of the data you used and (2) ``rocks`` and the underlying
:term:`SsODNet` service. Every observation and measurement in :term:`SsODNet` is
backed by at least one peer-rievewed publication which should be cited.

For (2), we would appreciate a reference to `Berthier+
2022 <https://arxiv.org/abs/2209.10697>`_ and a footnote to point the reader
to the ``rocks`` repository at `https://github.com/maxmahlke/rocks <https://github.com/maxmahlke/rocks>`_.

For (1), please see the description below.


.. _bibman:

Bibliography Management with ``rocks``
--------------------------------------

Giving credit where credit is due is straight-forward with ``rocks``: all parameters in the :term:`ssoCard`
and :term:`datacloud catalogues<Datacloud Catalogue>` contain their bibliographic references in the ``bibref``
entry. As values in the :term:`ssoCard` may be derived from multiple observations, the ``bibref`` attribute
of the ``Rock`` class parameters is a list.

.. tab-set::

   .. tab-item:: ssoCard

        The diameter of (2) Pallas given in the ssoCard is a weighted-mean of
        several published values, all of which are referenced.

        .. code-block:: python

            >>> import rocks
            >>> pallas = rocks.Rock(2)
            >>> pallas.diameter.bibref
            [Bibref(doi='10.1051/0004-6361/202141781', year=2021, title='VLT/SPHERE imaging survey of the largest main-belt asteroids: Final results and synthesis', bibcode='2021A&A...654A..56V', shortbib='Vernazza+2021'),
             Bibref(doi='10.1016/j.icarus.2009.08.007', year=2010, title='Physical properties of (2) Pallas', bibcode='2010Icar..205..460C', shortbib='Carry+2010a'),
             Bibref(doi='10.1038/s41550-019-1007-5', year=2020, title='The violent collisional history of aqueously evolved (2) Pallas', bibcode='2020NatAs...4..569M', shortbib='Marsset+2020'),
              Bibref(doi='10.1051/0004-6361/201629956', year=2017, title='Volumes and bulk densities of forty asteroids from ADAM shape modeling', bibcode='2017A&A...601A.114H', shortbib='Hanuš+2017a')]


   .. tab-item:: datacloud

        Datacloud catalogues are serialized as ``pandas`` ``DataFrame``. The bibliographic information
        is provided the ``shortbib`` and ``bibcode`` attributes.

        .. code-block:: python

            >>> import rocks
            >>> pallas = rocks.Rock(2, datacloud='diameters')
            >>> pallas.diameters.columns
            Index(['title', 'shortbib', 'bibcode', 'year', 'id_', 'number', 'name',
                   'diameter', 'err_diameter_up', 'err_diameter_down', 'albedo',
                   'err_albedo_up', 'err_albedo_down', 'beaming', 'err_beaming',
                   'emissivity', 'err_emissivity', 'selection', 'method',
                   'preferred_albedo', 'preferred_diameter', 'preferred'],
                  dtype='object')
            >>> pallas.diameters.shortbib
            0                 Herald+2019
            1                 Herald+2019
            2                   Ryan+2010
            3               Drummond+2008
            4               Tedesco+2002a
            5               Drummond+1989
            6               Drummond+2009
            7               Vernazza+2021
            8                 Carry+2010a
            9                   Usui+2011
            10               Marsset+2020
                      [...]
            Name: shortbib, dtype: object

The ``shortbib`` attribute of the ``bibref`` entries gives a legible list of source publications. The
``bibcode`` or ``doi`` attributes may be useful for bibliographic management in TeX publications.

.. code-block:: python

   >>> import rocks
   >>> pallas = rocks.Rock(2)
   >>> shortbibs = pallas.diameter.bibref.shortbib
   >>> bibcodes = pallas.diameter.bibref.bibcode
   >>> print(f"The diameter of (2) Pallas is based on work by {', '.join(shortbibs)}")
   The diameter of (2) Pallas is based on work by Vernazza+2021, Carry+2010a, Marsset+2020, Hanuš+2017a)
   >>> print("To cite: \cite{",  ','.join(bibcodes), '}')
   To cite: \cite{ 2021A&A...654A..56V,2010Icar..205..460C,2020NatAs...4..569M,2017A&A...601A.114H }

To get a specific bibliographic reference, we select it based on its index from the ``bibref`` list:

.. code-block:: python

   >>> pallas.diameter.bibref[0]
   Bibref(
     doi='10.1051/0004-6361/202141781',
     year=2021,
     title='VLT/SPHERE imaging survey of the largest main-belt asteroids: Final results and synthesis',
     bibcode='2021A&A...654A..56V',
     shortbib='Vernazza+2021'
   )
