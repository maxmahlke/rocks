#########
``rocks``
#########

.. raw:: html

    <style> .gray {color:#979eab} </style>

.. role:: gray

A ``python`` client to explore and retrieve asteroid data from `SsODNet
<https://ssp.imcce.fr/webservices/ssodnet/>`_. It serves to quickly get answers
to common questions as the ones below. All data is cited and new observations are ingested on a weekly basis.\ [#f1]_


.. |br| raw:: html

     <br>

.. highlight:: python

|br|

:octicon:`telescope;1em` **Idenfitication of minor bodies using** `quaero <https://ssp.imcce.fr/webservices/ssodnet/api/quaero/>`_.


.. grid:: 2

    .. grid-item-card::
      :link: cards-clickable
      :link-type: ref

      What is the number of ``Didymos``?
      What asteroid has the number ``594913``?


    .. grid-item-card::
      :link: cards-clickable
      :link-type: ref

      What aliases of ``2000 UD93`` are used in different databases?


|br|
:octicon:`beaker;1em` **Best estimates of dynamical and physical parameters from the** `ssoCard <https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/>`_.

.. grid:: 2

    .. grid-item-card::
      :link: cards-clickable
      :link-type: ref

      What is the albedo of ``(221) Eos``?


    .. grid-item-card::
      :link: cards-clickable
      :link-type: ref

      What is the distribution of thermal inertias of known Barbarian asteroids?

|br|
:octicon:`database;1em` **Full**\ [#f2]_ **literature overview with** `datacloud <https://ssp.imcce.fr/webservices/ssodnet/api/datacloud/>`_.

.. grid:: 2

    .. grid-item-card::
      :link: cards-clickable
      :link-type: ref

      What masses of ``(1) Ceres`` have been published? What are the measurement uncertainties and methods?


    .. grid-item-card::
      :link: cards-clickable
      :link-type: ref

      What taxonomic classifications of ``(214) Aschera`` have been proposed over time?

|br|
:octicon:`zap;1em` **And more!**

.. grid:: 2

    .. grid-item-card::
      :link: cards-clickable
      :link-type: ref

      Who was ``zappafrank``?

    .. grid-item-card::
      :link: cards-clickable
      :link-type: ref

      Is my data in `SsODNet <https://ssp.imcce.fr/webservices/ssodnet/>`_ and getting cited?

|br|

``rocks`` makes this information accessible in two ways: via the command line for quick
exploration and via ``python`` for scripted analysis. The syntax is simple and intuitive.

.. tab-set::

  .. tab-item:: Command Line

      .. code-block:: bash

          $ rocks id 221
          (221) Eos

          $ rocks class Eos
          MB>Outer

          $ rocks albedo Eos
          0.136 +- 0.004

          $ rocks masses Eos
          +---+-------------+-------------+---------------+---------+--------------+
          |   | mass        | err_mass_up | err_mass_down | method  | shortbib     |
          +---+-------------+-------------+---------------+---------+--------------+
          | 1 | 1.22125e+18 | 0.0         | 0.0           | EPHEM   | Folkner+2014 |
          | 2 | 2.39e+18    | 5.97e+17    | -5.97e+17     | DEFLECT | Goffin+2014  |
          | 3 | 1.04688e+18 | 5.16159e+17 | -5.16159e+17  | EPHEM   | Fienga+2019  |
          +---+-------------+-------------+---------------+---------+--------------+

  .. tab-item :: python


     .. code-block:: python

       >>> from rocks import Rock     # every asteroid is represented by a 'Rock' instance
       >>> ceres = Rock("ceres")      # retrieve ssoCard of (1) Ceres
       >>> ceres.diameter.value       # get the parameter values and metadata via the dot notation
       848.4
       >>> ceres.diameter.unit
       'km'
       >>> ceres.mass.value
       9.384e+20
       >>> ceres.mass.error
       6.711e+17
.. >>> ceres.mass.bibref[0].shortbib
.. 'Russell+2016'
.. >>> ceres = Rock("ceres", datacloud='taxonomies')      # add datacloud information
.. >>> ceres.taxonomies.class_.values
.. ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'G', 'G']
.. >>> ceres.taxonomies.shortbib.values
.. ['Bus&Binzel+2002', 'Lazzaro+2004', 'Fornasier+2014b', 'DeMeo+2009', 'Sergeyev+2022', 'Mahlke+2022', 'Lazzaro+2004', 'Tholen+1989', 'Fornasier+2014b']



.. Easy access of asteroid properties using the :ref:`Rock<rock_class>` class.
.. $ rocks taxonomies Eos
.. +---+--------+---------+--------+-----------+-----------+------------------+
.. |   | class_ | complex | method | waverange | scheme    | shortbib         |
.. +---+--------+---------+--------+-----------+-----------+------------------+
.. | 1 | S      | S       | Phot   | VIS       | Tholen    | Tholen+1989      |
.. | 2 | K      | K       | Spec   | VIS       | Bus       | Bus&Binzel+2002  |
.. | 3 | K      | K       | Spec   | VIS       | Bus       | MotheDiniz+2005  |
.. | 4 | K      | K       | Spec   | VISNIR    | Bus       | MotheDiniz+2008a |
.. | 5 | K      | K       | Spec   | VISNIR    | Bus-DeMeo | Clark+2009       |
.. | 6 | K      | K       | Spec   | VISNIR    | Bus-DeMeo | DeMeo+2009       |
.. | 7 | K      | K       | Spec   | VISNIR    | Mahlke    | Mahlke+2022      |
.. +---+--------+---------+--------+-----------+-----------+------------------+

.. $ rocks masses Eos
.. +---+-------------+-------------+---------------+---------+--------------+
.. |   | mass        | err_mass_up | err_mass_down | method  | shortbib     |
.. +---+-------------+-------------+---------------+---------+--------------+
.. | 1 | 1.22125e+18 | 0.0         | 0.0           | EPHEM   | Folkner+2014 |
.. | 2 | 2.39e+18    | 5.97e+17    | -5.97e+17     | DEFLECT | Goffin+2014  |
.. | 3 | 1.04688e+18 | 5.16159e+17 | -5.16159e+17  | EPHEM   | Fienga+2019  |
.. +---+-------------+-------------+---------------+---------+--------------+

.. via the Command Line
.. ====================

.. Quick exploration of asteroid parameters using the ``rocks`` :ref:`command-line interface<cli>`.


.. via a ``python`` script
.. =======================



.. **Disclaimer: The SsODNet service and its database are in an alpha version and
.. under constant revision.
.. The provided values and access methods may change
.. without notice.**


.. .. card:: Clickable Card (internal)
..     :link: cards-clickable
..     :link-type: ref

..     What is the best estimate of the albedo of (221) Eos?

.. .. card:: Clickable Card (internal)
..     :link: cards-clickable
..     :link-type: ref

..     What is the best estimate of the albedo of (221) Eos?




.. rubric:: Footnotes
   :caption:

.. [#f1] Latest version: 1.5.16  - `What's new? <https://github.com/maxmahlke/rocks/blob/master/CHANGELOG.md>`_  | Comment, bug or feature request? Open an issue on `GitHub <https://github.com/maxmahlke/rocks/issues>`_.
.. [#f2] That's what we are aiming for. Is there a data source you are missing? `Email us! <mailto:benoit.carry@oca.eu>`_

.. toctree::
   :maxdepth: 2
   :caption: Contents
   :hidden:

   Getting Started<getting_started>
   Available Data<ssodnet>
   Usage<cli>
   tutorials
   appendix
   glossary
