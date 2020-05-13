Names, Numbers, Designations
============================

SsODNet:quaero provides a fast, fuzzy-searchable index of current and previous
asteroid designations, names, and numbers. When combining large databases from
different years, e.g. SDSS MOC4 and VISTA MOVIS, the same asteroid may appear
with different designations. Quaero gives the list of aliases to identify
ambiguities and the execution time to comfortably execute it for hundreds of
thousands of objects. 

:: 

   $ rocks identify "2013 JJ2"            
   (nan) 2010 PA1

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

.. _identify:

.. autofunction:: get_name_number

When saving asteroid data, the name or designation is a handy unique identifier
for the filename. The whitespace in the designations is, however, not
convenient. The function below removes troublesome characters.

.. autofunction:: to_filename
