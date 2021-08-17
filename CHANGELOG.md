# 1.2.3
- Fail gracefully if no ssoCard is present for asteroid

# 1.2.2 - 2021-08-16
- Fixed unit lookup file
- Merge taxonomy entries in ssoCard if there are more than one
- Fixed missing dependencies and requirements
- Added compatibility with python3.7 by dropping the metalib dependency

# 1.2.1 - 2021-08-16
- Fixed bug in output of diamalbedos

# 1.2.0 - 2021-08-15
- Updated the pydantic model to reflect the new ssoCard structure
- The 'datacloud' argument of the Rock class now accepts the property name aliases of the catalogue names, eg: "albedos", "diameters" instead of "diamalbedo"
- Added new shortcuts: a,e,i/ap,ep,ip for the orbital/proper elements: "$ rocks ap Ceres"
- Querying asteroid properties from the command line which coincide with python keywords no longer results in an error (e.g. "rocks class Hebe")
- Added --version command

# 1.1.2 - 2021-05-18
- The 'albedos' and 'diameters' subsets of the 'diamalbedo' catalogue now have their
  own attributes in the Rock class
- Added return_id argument to 'identify'. By default, it now only returns name and number. To get the SsODNet ID, set return_id=True.

# 1.1.1 - 2021-05-17
- Added a prompt to download the index from the GitHub repo to the cache if not found at startup

# 1.1.0 - 2021-05-16
- Updated pydantic model to reflect new ssoCard structure
- The "Rock" class now takes a new "ssocard" parameter which can be
  passed ssoCards in form of dictionaries
- Added nested async support for jupyter notebooks
- Added cache clearing function

# 1.0.0 - 2021-02-15
- Made ssoCard queries asynchronous
- Switched to pydantic implementation of ssoCard

# 0.2.0 - 2021-02-14
- Added progressbar to rocks.identify
- Bugfix in cli module

# 0.1.2 - 2021-02-09
- rocks docs now points to the online documentation
- Bugfixes in the core module

# 0.1.1 - 2021-02-08
- Speed-up of local name resolution by refactoring the resolution logic
- Index file is no longer checked for date of last modification to reduce startup time

# 0.1 - 2021-02-07
- Initial release on PyPI
