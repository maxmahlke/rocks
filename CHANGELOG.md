# 1.9.2 -
- Fix display of empty datacloud catalogues
- Sort mpcatobs by date_obs when printing

# 1.9.1 - 2023-12-11
- Fix types of datacloud colors properties

# 1.9 - 2023-12-06
- Make cache directory configurable using the ``ROCKS_CACHE_DIR`` environment variable
- Add cache-less mode (`ROCKS_CACHE_DIR='no-cache'`) where all queries are done via SsODNet and no result is stored
- Add more reasonable timeouts for asynchronous queries

# 1.8.13 - 2023-11-16
- Add more readable output for spin queries (#25)
- Remove upper python version limit
- Remove documentation dependencies from pip install

# 1.8.12 - 2023-11-14
- load_bft now passes kwargs to read_parquet
- rocks no longer exits if the index is malformed (#27)
- Fix bug in datacloud table display (#28)
- Add work-around for invalid period_flag type (#28)

# 1.8.11 - 2023-10-13
- rocks no longer exits if a number look-up fails

# 1.8.10 - 2023-09-27
- Load a smaller version of BFT by default by using a column subset
- Update the BFT when selecting 'Update data' option in `$ rocks status`
- Get list of recently named asteroids from WGSBN instead of comparing indices
- Store citations in cache to increase look-up speed
- Fix types of Spins datacloud catalogue

# 1.8.9 - 2023-09-11
- Move to pydantic v2
- Fix bug which prevented updating phase_function datacloud catalogues

# 1.8.8 - 2023-08-29
- Add BFT support: `rocks.load_bft()` and more, see documentation

# 1.8.7 - 2023-08-16
- Add bibref and method to pair
- Fix bibref type of tisserand_parameter

# 1.8.6 - 2023-08-16
- Fix access of tisserand_parameter and pair
- Fix bibref type in yarkovsky and proper_elements
- Fix output of pairs datacloud table
- Catch failed alias look-up in `$ rocks ids` call

# 1.8.5 - 2023-06-29
- Add '$ rocks recent' command to echo recently named asteroids after updating index
- Fix bug in inventory function

# 1.8.4 - 2023-06-16
- Add 'Rock.get_parameter' method which accepts string values to look up parameters:
      rocks.Rock(1).get_parameter('taxonomy.class_.value')
  Good for iterating over many parameters.

- Fix parameter shortcut and unit look-up for MOIDs

# 1.8.3 - 2023-06-16
- Rename min/max error levels from min_/max_ to min/max. These terms are not python keywords.

# 1.8.2 - 2023-06-02
- Alias query is now done remotely via quaero. Removing the alias index, it's slow and heavy.
- Speed up index creation using multiprocessing

# 1.8.1 - 2023-05-25
- Fix install bug by providing numpy version markers

# 1.8 - 2023-05-25
- Support python3.11
- Make all ssoCard bibref properties ListWithAttributes

# 1.7.8 - 2023-05-04
- Add Johnson R filter to phase functions entries
- No longer storing invalid datacloud responses

# 1.7.7 - 2023-04-24
- Name resolution strip leading/trailing whitespace from identfier
- Promote mal-formed ssoCard error message

# 1.7.6 - 2023-04-21
- Update ssoCard format for ssoCard version 1.1.0
- Update the metadata and dataset JSONs when choosing 'update' in '$ rocks status'
- Strip diacritics from author search when running '$ rocks author'
- Catch invalid datacloud response when querying catalogues
- Catch malformed index when running rocks status

# 1.7.5 - 2023-03-09
- Change type of spins.period_flag to reflect upstream change

# 1.7.4 - 2023-03-05
- Move index check from init to into name resolution module as proposed in #21

# 1.7.3 - 2023-02-20
- Fix column name in diameters echo (#20)
- Add boolean property for families: bool(rocks.Rock(1).family) is True if
  family.name is not ""

# 1.7.2 - 2023-02-13
- Update rich dependency requirement to make rocks compatible with classy

# 1.7.1 - 2023-02-08
- Inform about malformed ssoCard at debug rather than warning level
- Remove lines where albedo|diameter are NaN when querying albedos|diameters on
  command line
- Differentiate between malformed index and request for asteroid number larger than the maximum number of all asteroids

# 1.7.0 - 2023-02-03
- Improve compatibility with Mac, add compatibility with Windows. Use appdirs
  package to use system-dependent cache directory:

  Windows: ':\\Users\\$USER\\AppData\\Local\\rocks\\Cache'
  Mac: '/Users/$USER/Library/Caches/rocks'
  Linux: '$HOME/.cache/rocks'

  Mac users of previous rocks versions can remove the '$HOME/.cache/rocks' directory.

# 1.6.16 - 2023-01-25
- Remove deprecated suppress_errors argument from CLI call (#19)
- Make albedo.bibref a list of Bibref rather than a list of dict

# 1.6.15 - 2023-01-19
- Expose the logging-level of rocks with the rocks.set_log_level function
- Remove the suppress_errors argument of rocks.Rock and rocks.rocks -> use rocks.set_log_level instead

# 1.6.14 - 2023-01-08
- Make rocks behave well in multithreaded applications (#18)

# 1.6.13 - 2023-01-06
- Bugfix in outdated-rocks message

# 1.6.12 - 2022-12-19
- Fix bug in mpcatobs datacloud catalogue
- More robust detection of malformed datacloud catalogues

# 1.6.11 - 2022-11-30
- rocks.id and rocks.rocks support pd.Series input again
- Faster index creation (4min -> 1min, YMMV)
- Add "on_404" argument to rocks.Rock and rocks.rocks (#16)

# 1.6.10 - 2022-11-17
- Fix retrieval of ssoCards

# 1.6.9 - 2022-11-17
- Fixed empty lines spam in jupyter notebook
- rocks logger format is only applied to rocks logger, not to all modules

# 1.6.8 - 2022-11-16
- YA bug in datacloud entry ingestion (#15)

# 1.6.7 - 2022-11-14
- Fixed bug in datacloud entry ingestion (#14)

# 1.6.6 - 2022-11-13
- Fixed bug in index-existence check on startup
- Fixed missing imports in index creation routine

# 1.6.5 - 2022-11-08
- Code refactored to optimize performance of CLI, e.g. $ rocks id is now 2x faster
- identify() no longer accepts pd.Series to avoid heavy pandas import
- Adding '--clear' and '--update' flags to $ rocks status
- $ rocks author output now includes bibcode
- Switching from warnings to logging module
- Fix bug in datacloud families ingestion

# 1.6.4 - 2022-10-21
- Add 'author' command to quickly check the presence of data from peer-reviewed article: '$ rocks author bowell'
- bool(rocks.Rock(<id>).color.<filter>) is True if color.<filter>.value is finite

# 1.6.3 - 2022-10-12
- Add nicer representation of colors '$ rocks color tina', '$ rocks color.g_i tina'
- Fix bug in case ssoCard query returns null
- Fix bug in bibref implementation

# 1.6.2 - 2022-10-05
- Parameters of different spin solutions / bibref entries are now accessible via
  the common dot notation, see version 1.6.2
  https://rocks.readthedocs.io/en/latest/cli.html#bibliography-management-with-rocks
  or '$ rocks diameter.bibref.shortbib pallas'
- Added shortcuts for equation-of-state vector

# 1.6.1 - 2022-10-04
- Fix in lru_cache call to work with python3.7

# 1.6.0 - 2022-10-03
- New access model for metadata attributes (format, description, symbol, label, and unit):
  accessed dynamically and hidden in output (except for unit)
- Fix phase_function output once again
- Fix datacloud spin catalogue ingestion

# 1.5.17 - 2022-09-30
- Fix output of phase_functions, yarkovskys, and binaries datacloud catalogues
- Change parameter echo method to regular 'print' as rich outputs '__repr__' instead of '__str__'

# 1.5.16 - 2022-09-29
- Documentation now even better looking. Also more up-to-date.
- Add alias 'rocks.id' for 'rocks.identify' in python interface
- Datacloud phase_functions no longer hide ssoCard phase_function
- Added shortcuts for phase_function filters:
  - phase_function.generic_johnson_V -> phase_function.V
  - phase_function.misc_atlas_cyan -> phase_function.cyan
  - phase_function.misc_atlas_orange -> phase_function.orange
- Added summary output for phase_function ('$ rocks phase_function eos')
- Added summary output for phase_function.filter ('$ rocks phase_function.cyan eos')
- Added boolean properties to phase_function and phase_function.filter ('if rock.phase_function' is True if
  an absolute magnitude is present in any filter)
- Bugfix in aliases look-up in case of None
- Bugfix in selection of preferred observations in weighted average

# 1.5.15 - 2022-09-22
- Bugfix in datacloud and selection echo
- Rename 'aliases' to 'ids'

# 1.5.14 - 2022-09-22
- Add shortcut P for orbit
- SpinList is never empty, it gets populated with an empty Spin object in case of missing spin information in ssoCard
- SpinList is False if all period entries in the list are NaN
- Fix verbose parameter output
- Remove description and label entries from 'links' parameters

# 1.5.13 - 2022-09-01
- Parameter echo to console now respects the -v|--verbose flag
- Fix implementation of dynamical parameters

# 1.5.12 - 2022-08-25
- Get preferred entries from the ssoCard instead of hardcoded decision trees
- Remove definitions module
- Fix printing of astorb, mpcorb catalogues
- Fix in ssoCard ingestion in case of missing spins

# 1.5.11 - 2022-08-10
- Implement metadata attributes like .unit and .description
- Added catch for missing index files

# 1.5.10 - 2022-08-03
- Added "who" CLI command to look up citation associated to named asteroid
- Added interactive search using optional fzf tool
- Simplified "rocks status" output
- Updated SsoCard attributes following upstream changes
- Removed CLASS_TO_COMPLEX dictionary: complex is given in SsODNet

# 1.5.9 - 2022-07-11
- Fix highlighting of best-estimate parameters in datacloud queries
- Fix bug in datacloud catalogue update

# 1.5.8 - 2022-07-03
- Added bibcode and doi to datacloud entries

# 1.5.7 - 2022-06-29
- Fixed bug in preferred-attribute-highlighting

# 1.5.6 - 2022-06-24
- Updated Pair implementation
- Bugfix in ssoCard spin implementation

# 1.5.5 - 2022-06-22
- Fixed implementation of thermal inertia, absolute magnitude, spins, and proper elements
- Fixed implementation of thermal inertias and spins (ie the datacloud attributes)

# 1.5.4 - 2022-05-17
- Update the metadata json url
- Pretty-print tracebacks with rich

# 1.5.3 - 2022-05-10
- Fix bug in cache inventory function

# 1.5.2 - 2022-05-10
- Update implementation of absolute magnitude in ssoCard following upstream change

# 1.5.1 - 2022-05-03
- Fixed implementation of parameter unit
- Implemented boolean property of Value: "bool(rocks.Rock(1).albedo)" is True if the albedo.value is not NaN, else False

# 1.5.0 - 2022-04-26
- Updated Rock class to reflect upstream changes in ssoCard structure
- Updated datacloud classes to reflect upstream changes in datacloud catalogue structures
- Improved rocks version comparison
- Add catch for 594913 'Aylo'chaxnim in index lookup
- Added shortcut "D" for diameter
- Removed the "units" argument from "rocks parameters", units are now printed by default
- Add catch for malformed datacloud catalogues

# 1.4.24 - 2022-04-25
- Fix implementation of diamalbedo catalogue

# 1.4.23 - 2022-04-02
- Fixed incorrect display of double-letter taxonomic classes on command line
- Index for asteroids with designation 2022 is now correctly compiled

# 1.4.22 - 2022-04-01
- Updated taxonomy implementation to reflect change in ssoCard
- Set all colour values to "grayish" and shapes to "roughly potato-like"

# 1.4.21 - 2022-03-30
- Bugfix in datacloud catalogue retrieval

# 1.4.20 - 2022-03-28
- Properly catch empty JSON responses stored as ssocards or datacloud catalogues
- Updated color entries in ssoCard and datacloud. datacloud 'colors' no longer shadows the ssoCard 'colors' as the latter
  has been renamed to 'color'

# 1.4.19 - 2022-03-26
- Implement upstream change to fix storing of ssocards and datacloud catalogues

# 1.4.18 - 2022-03-23
- Add -v|--verbose flag to parameter queries on the command line. Errors in the ssoCard
  structure are suppressed unless the verbose flag is set.

# 1.4.17 - 2022-03-23
- Add "suppress_errors" argument to rocks.rocks and rocks.Rock. If True, errors in the ssoCard JSON are not printed
  when creating the Rock instances. Default is False, errors are printed.
- Updated structure of Pairs datacloud catalogue

# 1.4.16 - 2022-03-10
- Add "complex" keyword to taxonomy
- Change "complex_" to "complex" in the taxonomies datacloud catalogue as it is not a protected python keyword

# 1.4.15 - 2022-03-01
- Fix in name resolution which caused degeneracy with packed permanent
  designation format

# 1.4.14 - 2022-02-12
- Updated implementation of asteroid pair to reflect change in ssoCard
- Added the error_ attributes to Values. It contains the mean of the absolute values of the min and max error.
- Added 'aliases' command in CLI to echo asteroid aliases
- Cached ssoCards are now dereferenced to the actual level of the ssoCard

# 1.4.13  - 2022-02-02
- Added the -u/--units argument to the "parameters" CLI command to echo the
  units

# 1.4.12 - 2022-01-27
- Bugfix in index creation, designation file was showing number
- Bugfix in datacloud masses catalogue

# 1.4.11 - 2022-01-26
- Added a failsafe for broken Spin entries which pydantic cannot handle

# 1.4.10 - 2021-12-21
- Decreased execution time on command line by splitting index file and
  lazy-loading the plots module
- The previous index.pkl is now split into many smaller files living in
  $HOME/.cache/rocks/index

# 1.4.9 - 2021-12-14
- Added the short index containing only asteroids with number up to
  10,000. Command line queries will first check this index, which saves about
  0.5s in case of a successful resolution and carries a negligible time penalty
  on an unsuccessful one.
- Multiple parameters can now be queried via the CLI by chaining them with commas: $ rocks ap,ep pallas
- Added alias for sine of proper inclination: sinip

# 1.4.8 - 2021-12-08
- Reduced startup time by 50% by reducing the size of the asteroid name-number index

# 1.4.7 - 2021-12-05
- Added the Tisserand parameter to the ssoCard
- Rock.parameters.physical.spin is now a list of Spin instances, rather than a
  Spin instance with lists. This is consistent with the Rock.parameters.physical.taxonomy parameter.
- If multiple taxonomic classifications exist, rocks will now print the class and the shortbib
- Datacloud properties are now sorted by year of publication when echoed on the command line

# 1.4.6 - 2021-11-28
- Rocks can now be created even if part of the ssoCard is invalid. An erroneous
  albedo entry does not prevent retrieving the diameter anymore.
- If the query of a named asteroid via the CLI fails, rocks proposes some
  matches
- Reduced verbosity of output if name resolution fails during parameter query
- Added timeout to rocks version check

# 1.4.5 - 2021-11-24
- Updated diamalbedo catalogue structure

# 1.4.4 - 2021-11-17
- Bugfix in ssodnet module
- Empty datacloud catalogues are now cached as well to reduce redundant queries
- More fixes for the Spin parameter

# 1.4.3 - 2021-11-04
- Added command alias: update -> status
- The phase-function parameter is now correctly called phase_function
- The phase-function datacloud catalogue parameter is now correctly called phase_functions
- Aligned implementation of Spin parameter with ssoCard changes

# 1.4.2 - 2021-11-03
- Adapted GREETING to supervisor's liking
- Improved "missing ssoCard" error message
- Do not cache empty ssoCards
- Fixed bug which prevented usage of cached ssoCards

# 1.4.1 - 2021-10-26
- Bugfix in confirm_identity
- Bugfix in core

# 1.4.0 - 2021-10-25
- The asteroid name-number index file is now compiled on SsODNet side. It is removed from the GitHub repo.
- Added Density parameter to Rock
- Added greeting which is displayed when index.pkl is missing
- Added aliases for commands id (identify) and parameters (parameter)
- Fixed bug in units display
- Fixed bugs in rocks parameters
- Fixed bugs in rocks status

# 1.3.5 - 2021-10-22
- Fixed issue with rocks.rocks looking for ssoCards which do not exist

# 1.3.4 - 2021-10-22
- Bugfix in index retrieval function

# 1.3.3 - 2021-10-22
- Better display of index modification time in rocks status command
- Ensuring that method and bibref are always lists in albedo

# 1.3.2 - 2021-10-17
- Updated datacloud catalogue implementations
- Catching the 502 server error with rocks identify
- Stripping surrounding whitespace from passed asteroid identifiers
- Added "reduced" identifier to index for more reliable local name resolution (e.g. "riodejaneiro")
- Reformatted the resolver module
- rocks update now offers to clear the cache
- rocks update now correctly checks both the ssocard.version and ssocard.datetime to find outdated cards
- rocks update now echos the last-modified date of the index and the cached metadata files
- Added clear_cache function to utils module
- More accurate estimation of remaining name resolution time
- Unknown commands on the CLI are now recognized.
- Renamed rocks update to rocks status
- Made rocks status output more consistent
- Removed tqdm dependency
- Made rocks.rocks asynchronous
- Renamed 'no_cache' keyword to 'local' for consistency

# 1.3.1 - 2021-09-14
- datacloud catalogues and ssoCards are now updated asynchronously
- identify now correctly checks the 'id' column of the returned json response
- User has to confirm update of ssoCards
- Overall nicer rocks update dialogue

# 1.3.0 - 2021-09-14
- datacloud catalogues are now DataCloudDataFrame objects: a pd.DataFrame subclass with added .plot() and .weighted_average()
- Readded the --plot flag for datacloud CLI queries
- Merged the 'rocks status' command into the 'rocks update' command
- The 'rocks update' command now updates all cached data if requested
- Switched the local index from a pandas dataframe to dictionaries
- Included the absolute magnitude into the ssoCard following upstream development
- Local name resolution is now lightning fast
- Removed outdated code and reformatted the utils module
- Lots of documentation edits
- The diamalbedo catalogue once again has the preferred attribute
- Bugfix in the weighted_average calculation
- Made the wording more consistent: asteroid "property" -> asteroid "parameter"
- Added no_cache keyword to datacloud catalogue queries

# 1.2.3 - 2021-09-08
- Fail gracefully if no ssoCard is present for asteroid when querying datacloud catalogue
- Added weighted average output to some datacloud catalogue queries from the command line
- Added weigthed_average method to Datacloud catalogue class
- Print warning when no ssoCard could be retrieved for an asteroid.
- Added 'no_cache' keyword to 'rocks.ssodnet.get_ssocard'. If True, it forces the remote query of the ssoCard
- Improved 'rocks status' command to echo the number of cached ssoCards and offer to update the out-of-date ones
- Fixed typo in ssodnet name of astorb catalogue
- Fixed output of datacloud parameters with CLI
- rocks.rocks now supports passing a single id (though you should use rocks.Rock instead)
- Correct handling of all-zero numerical properties in datacloud catalogues

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
