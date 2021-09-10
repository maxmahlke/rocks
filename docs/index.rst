``rocks``
=========
*for space rocks*

A ``python`` package to query and explore asteroid data from
`SsODNet <https://ssp.imcce.fr/webservices/ssodnet/>`_.

**Disclaimer: The SsODNet service and its database are in an alpha version and
under constant revision. The provided values and access methods may change
without notice.**


Latest version: 1.3.0  - `What's new? <https://github.com/maxmahlke/rocks/blob/master/CHANGELOG.md>`_

via the Command Line
--------------------

Quick exploration of asteroid parameters using the :ref:`rocks<Command-Line Interface>` command-line interface.

.. code-block:: bash       
                           
   $ rocks identify 221    # you can also just use "id"
   (221) Eos               

   $ rocks class Eos
   MB>Outer

   $ rocks albedo Eos
   0.136 +- 0.004

   $ rocks taxonomy.class_ Eos
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

   $ rocks masses Eos
    +----------+----------+---------+-------------+------+
    | mass     | err_mass | method  | shortbib    | year |
    +----------+----------+---------+-------------+------+
    | 2.39e+18 | 5.97e+17 | DEFLECT | Goffin+2014 | 2014 |
    +----------+----------+---------+-------------+------+



via a ``python`` script
-----------------------

Easy access of asteroid properties using the :ref:`Rock<rock_class>` class.

.. code-block:: python     
                           
  >> from rocks import Rock
  >> ceres = Rock("ceres") 
  >> ceres.diameter.value
  848.4                    
  >> ceres.mass.value
  9.384e+20                
  >> ceres.mass.error
  6.711e+17

See more use cases in the :ref:`Tutorials<Tutorials>`.

.. toctree::
   :maxdepth: 1
   :caption: Contents
   :hidden:

   Introduction<index>
   Getting Started<getting_started>
   Available Data<ssodnet>
   The python package<core>
   Command Line Interface<cli>
   tutorials
