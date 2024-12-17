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

:octicon:`telescope;1em` **Identification of minor bodies using** `quaero <https://ssp.imcce.fr/webservices/ssodnet/api/quaero/>`_.


.. grid:: 2

    .. grid-item-card::
      :link: name_resolution
      :link-type: ref

      What is the number of ``Didymos``?
      What asteroid has the number ``594913``?


    .. grid-item-card::
      :link: aliases
      :link-type: ref

      What aliases of ``2000 UD93`` are used in different databases?


|br|
:octicon:`beaker;1em` **Best estimates of dynamical and physical parameters from the** `ssoCard <https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/>`_.

.. grid:: 2

    .. grid-item-card::
      :link: getting_values
      :link-type: ref

      What is the albedo of ``(221) Eos``?


    .. grid-item-card::
      :link: thermal_barbarians
      :link-type: ref

      What is the distribution of thermal inertias of known Barbarian asteroids?

|br|
:octicon:`database;1em` **Complete**\ [#f2]_ **literature overview with** `datacloud <https://ssp.imcce.fr/webservices/ssodnet/api/datacloud/>`_ **and the** `ssoBFT <https://ssp.imcce.fr/webservices/ssodnet/api/ssobft/>`_.

.. grid:: 2

    .. grid-item-card::
      :link: masses_ceres
      :link-type: ref

      What masses of ``(1) Ceres`` have been published by whom?

    .. grid-item-card::
      :link: bft_example
      :link-type: ref

      Two lines for one table of ~720,000,000 minor body parameters.

    .. .. grid-item-card::
    ..   :link: datacloud_example
    ..   :link-type: ref
    ..
    ..   What taxonomic classifications of ``(214) Aschera`` have been proposed over time?

|br|
:octicon:`zap;1em` **And more!**

.. grid:: 2

    .. grid-item-card::
      :link: who
      :link-type: ref

      Who was ``zappafrank``?

    .. grid-item-card::
      :link: author
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

.. rubric:: Footnotes

.. [#f1] Latest version: 1.9.12  - `What's new? <https://github.com/maxmahlke/rocks/blob/master/CHANGELOG.md>`_  | Comment, bug or feature request? Open an issue on `GitHub <https://github.com/maxmahlke/rocks/issues>`_.
.. [#f2] That's what we are aiming for. Is there a data source you are missing? `Email us! <mailto:benoit.carry@oca.eu>`_

.. toctree::
   :maxdepth: 2
   :caption: Contents
   :hidden:

   Home<self>
   Getting Started<getting_started>
   Available Data<ssodnet>
   Basic Usage<cli>
   credit
   tutorials
   appendix
   glossary
