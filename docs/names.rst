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

The ``names.get_name_number`` method is a Quaero wrapper.

.. currentmodule:: names

.. _identify:

.. autofunction:: get_name_number

When saving asteroid data, the name or designation is a handy unique identifier
for the filename. The whitespace in the designations is, however, not
convenient. The function below removes troublesome characters.

.. autofunction:: to_filename
