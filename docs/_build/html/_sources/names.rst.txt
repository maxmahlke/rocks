Resolving names, numbers, designations
====================================== 
``rocks`` resolves identifying strings or numbers into the official number-name
pairs of minor bodies. Local lookups are emphasized by reformat input strings 
with regular expressions (e.g. ``'2014_yc62'`` -> ``'2014 YC62'``).
If the identifier cannot be resolved locally, ``SsODNet:quaero`` is queried.

``SsODNet:quaero`` keeps track of alias names, which comes in handy when
combining databases (e.g. *SDSS MOC4* and *VISTA MOVIS*).

Use cases and examples
""""""""""""""""""""""

**Quick lookups of asteroid names and numbers**, via the command line. See
:ref:`rocks identify <cli-identify>`.

.. code-block:: bash

   $ rocks identify "Rio de Janeiro"            
   (11334) Rio de Janeiro

**Multiprocessed lookup of many asteroid identifiers**, scripted. See the get_name_number_
function.

.. code-block:: python

   from rocks import names

**Merging databases containing alias names and distinct identifier formats**, scripted.
See the get_name_number_ function.

.. code-block:: python

   import pandas as pd

   from rocks import names

   # Two databases with asteroids and associated magnitudes
   db1 = pd.DataFrame(data={'designation': ['2013JJ2', 'de Broglie'],
                            'mV': [17, 15]})
   db2 = pd.DataFrame(data={'designation': ['Vermeer', '2010_pa1', 'de Broglie'],
                            'mB': [16.3, 18.1, 15.2]})

   # Merge them
   merged = pd.merge(db1, db2, left_on='designation',
                     right_on='designation', how='outer')

   #  designation    mV    mB
   #      2013JJ2  17.0   NaN
   #   de Broglie  15.0  15.2
   #      Vermeer   NaN  16.3
   #     2010_pa1   NaN  18.1

   # Query name and number with rocks
   names_numbers = names.identify(merged['designation'], parallel=2,
                                  verbose=False, progress=False) 
   merged['name'], merged['number'] = zip(*names_numbers)
   merged = merged.drop(columns=['designation'])

   #       name   number   mV    mB  
   #   2010 PA1      NaN 17.0   NaN  
   # de Broglie  30883.0 15.0  15.2  
   #    Vermeer   4928.0  NaN  16.3  
   #   2010 PA1      NaN  NaN  18.1  

   # Two of them are the same object. Collapse rows
   merged = merged.groupby('name', as_index=False).last()

   #       name   number    mB    mV
   #   2010 PA1      NaN  18.1  17.0
   #    Vermeer   4928.0  16.3   NaN
   # de Broglie  30883.0  15.2  15.0


Control flow of name resolution
"""""""""""""""""""""""""""""""

Some design choices:

- Always return a tuple
- Return number, name
- Return types are int, str when possible
- If asteroid is not numbered, return np.nan
- If identifier could not be resolved, return (None, None)
- Name queries are cached at runtime

.. graphviz::
    :name: name_resolution
    :caption: Flowchart for resolution of asteroid identifier to Number-Name pair.
              Hover over steps to get more information.
    :align: center

    digraph G {
          cli [label="Command Line", tooltip="rocks identify"];
          script [tooltip="rocks.name.identify()", label="Script"];
          identifier [shape=polygon, skew=0.2, fontname=Courier, label="Identifier",
                       width=1.4, fixedsize=true, tooltip="'2004es' 4, 'ceres'"];
          bouncer [shape=diamond, height=1, label="Valid Identifier",
                   tooltip="isinstance(id_, (str, int, float)"];
          formatting [shape=box, label="Formatting",
                      tooltip="Find type of identifier with regex, ensure proper format"];
          wrongid [shape=plaintext, fontname=Courier, label="return None, None"];
          format [shape=diamond, height=1, label="Recognized Format", tooltip="Name, Designation, Comet"];
          local [shape=folder, label="Local Index", tooltip="rocks index"];
          remote [shape=polygon, label="SsODNet", tooltip="Result is cached at runtime"];
          found [shape=diamond, height=1, label="Lookup Successful", tooltip=""];
          good [shape=plaintext, fontname=Courier, label="return number, name"];
          identified [shape=diamond, height=1, label="Identified", tooltip=""];
    
          cli -> identifier;
          script-> identifier;
          identifier -> bouncer;
          bouncer -> formatting [label=True, fontname=Courier];
          bouncer -> wrongid [label=False, fontname=Courier];
          formatting -> format;
          format -> local [label=True, fontname=Courier];
          format -> remote [label=False, fontname=Courier];
          local -> found;
          found -> good [label=True, fontname=Courier];
          found -> remote [label=False, fontname=Courier];
          remote -> identified;
          identified -> good [label=True, fontname=Courier];
          identified -> wrongid [label=False, fontname=Courier];
    
     }

The ``names.get_name_number`` function first tries to do a local lookup of the
asteroid identifier, using the index file. If this fails, it queries Quaero. 
The results are cached during runtime to profit from repeated queries.
It offers multiprocessing the queries.

The query speed largely depends on the number of successful local lookups.
Asteroid numbers should be prioritized as identifiers. A small benchmark using 260,000 lines from the SDSS MOC4:

- Serial mode: 80 queries / s 
- Parallel mode (4 cores): 380 queries / s
- Parallel mode (8 cores): 870 queries / s

.. currentmodule:: names

.. _get_name_number:

.. autofunction:: get_name_number

When saving asteroid data, the name or designation is a handy unique identifier
for the filename. The whitespace in the designations is, however, not
convenient. The function below removes troublesome characters.

.. autofunction:: to_filename

     ..digraph "sphinx-ext-graphviz" {
         ..size="6,4";
         ..rankdir="LR";
         ..graph [fontname="Verdana", fontsize="12"];
         ..node [fontname="Verdana", fontsize="12"];
         ..edge [fontname="Sans", fontsize="9"];

         ..sphinx [label="Sphinx", shape="component",
                 ..href="https://www.sphinx-doc.org/",
                 ..target="_blank"];
         ..dot [label="GraphViz", shape="component",
              ..href="https://www.graphviz.org/",
              ..target="_blank"];
         ..docs [label="Docs (.rst)", shape="folder",
               ..fillcolor=green, style=filled];
         ..svg_file [label="SVG Image", shape="note", fontcolor=white,
                   ..fillcolor="#3333ff", style=filled];
         ..html_files [label="HTML Files", shape="folder",
                     ..fillcolor=yellow, style=filled];

         ..docs -> sphinx [label=" parse "];
         ..sphinx -> dot [label=" call ", style=dashed, arrowhead=none];
         ..dot -> svg_file [label=" draw "];
         ..sphinx -> html_files [label=" render "];
         ..svg_file -> html_files [style=dashed];
     ..}
