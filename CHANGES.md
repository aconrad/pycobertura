# Release Notes

## Unreleased

## 2.0.1 (2021-01-20)

* Drop the `colorama` dependency in favor of hardcoded ANSI escape codes.
  Thanks @luislew

## 2.0.0 (2020-09-03)

* BACKWARD INCOMPATIBLE: The class `Cobertura` no longer instantiates a default
  `FileSystem` object if none is provided in the constructor
  `Cobertura.__init__(filesystem=...)`. If the content of files is accessed
  (e.g. to render a full coverage report) then a `FileSystem` instance must be
  provided.
* The class `Cobertura` will raise `MissingFileSystem` if no
  `FileSystem` object was provided via the keyword argument
  `Cobertura(filesystem=...)`. It will only be raised when calling methods that
  attempt to read the content of files, e.g. `Cobertura.file_source(...)` or
  `Cobertura.source_lines(...)`.

## 1.1.0 (2020-08-26)

* Support loading Cobertura reports from an XML string. Thanks @williamfzc
* Fix (or add?!) support for providing file objects to `Cobertura`.

## 1.0.1 (2020-07-08)

* Fix misreported coverage when a single coverage file is used with
  `pycobertura diff` to overlay covered and uncovered changes between two
  different sources. Thanks @bastih

## 1.0.0 (2020-06-21)

* Let the caller customize the appearance of the HTML report providing a
  `title`, omitting the rendering of sources by means of the boolean
  `render_file_sources` and providing an helpful message to the end-users (in
  place of the sources) by means of the `no_file_sources_message` parameter.
  Contributed by @nilleb.
* Add a `GitFilesystem` to allow pycobertura to access source files at different
  revisions from a git repository. Thanks @nilleb.
* BACKWARDS INCOMPATIBLE: Change the signature of the Cobertura object in order
  to accept a filesystem.
* BACKWARDS INCOMPATIBLE: Drop support for Python 2.
* Added tox task `black`, to use the the uncompromising Python code formatter.
  See https://black.readthedocs.io/en/stable/ to learn more about black. Thanks
  @nilleb.

## 0.10.5 (2018-12-11)
* Use a different `memoize()` implementation so that cached objects can be
  freed/garbage collected and prevent from running out of memory when processing
  a lot of cobertura files. Thanks @kannaiah

## 0.10.4 (2018-04-17)
* Calculate the correct line rate for diffs (#83). Previously
  `CoberturaDiff.diff_line_rate` with no filename argument would total up the
  different line rate changes from all of the modified files, which is not the
  correct difference in line rates between all files. Now the difference in line
  rate from the two reports objects will be directly used if no argument is
  passed. (@borgstrom)

## 0.10.3 (2018-03-20)
* Update author/repository info
* Update release script to use twine

## 0.10.2 (2018-03-20)
* Avoid duplicate file names in files() (#82). Some coverage reports include
  metrics for multiple classes within the same file and redundant rows would be
  generated for such reports. Thanks James DeFelice! (@jdef)

## 0.10.1 (2017-12-30)
* Drop support for Python 2.6
* Fix a `IndexError: list index out of range` error by being less specific about
  where to find `class` elements in the Cobertura report.

## 0.10.0 (2016-09-27)
* BACKWARDS INCOMPATIBLE: when a source file is not found in disk pycobertura
  will now raise a `pycobertura.filesystem.FileSystem.FileNotFound` exception
  instead of an `IOError`.
* possibility to pass a zip archive containing the source code instead of a
  directory
* BACKWARDS INCOMPATIBLE: Rename keyword argument `Cobertura(base_path=None)` >
  `Cobertura(source=None)`
* Introduce new keyword argument `Cobertura(source_prefix=None)`
* Fix an `IOError` / `FileNotFound` error which happens when the same coverage
  report is provided twice to `pycobertura diff` (diff in degraded mode) but the
  first code base (`--source1`) is missing a file mentioned in the coverage
  report.
* Fix a rare bug when diffing coverage xml where one file goes from zero lines
  to non-zero lines.

## 0.9.0 (2016-01-29)
* The coverage report now displays the class's filename instead of the class's
  name, the latter being more subject to different interpretations by coverage
  tools. This change was done to support coverage.py versions 3.x and 4.x.
* BACKWARDS INCOMPATIBLE: removed `CoberturaDiff.filename()`
* BACKWARDS INCOMPATIBLE: removed the term "class" from the API which make it
  more difficult to reason about. Now preferring "filename":

    - `Cobertura.line_rate(class_name=None)` > `Cobertura.line_rate(filename=None)`
    - `Cobertura.branch_rate(class_name=None)` > `Cobertura.branch_rate(filename=None)`
    - `Cobertura.missed_statements(class_name)` > `Cobertura.missed_statements(filename)`
    - `Cobertura.hit_statements(class_name)` > `Cobertura.hit_statements(filename)`
    - `Cobertura.line_statuses(class_name)` > `Cobertura.line_statuses(filename)`
    - `Cobertura.missed_lines(class_name)` > `Cobertura.missed_lines(filename)`
    - `Cobertura.class_source(class_name)` > `Cobertura.file_source(filename)`
    - `Cobertura.total_misses(class_name=None)` > `Cobertura.total_misses(filename=None)`
    - `Cobertura.total_hits(class_name=None)` > `Cobertura.total_hits(filename=None)`
    - `Cobertura.total_statements(class_name=None)` > `Cobertura.total_statements(filename=None)`
    - `Cobertura.filepath(class_name)` > `Cobertura.filepath(filename)`
    - `Cobertura.classes()` > `Cobertura.files()`
    - `Cobertura.has_classfile(class_name)` > `Cobertura.has_file(filename)`
    - `Cobertura.class_lines(class_name)` > `Cobertura.source_lines(filename)`
    - `CoberturaDiff.diff_total_statements(class_name=None)` > `CoberturaDiff.diff_total_statements(filename=None)`
    - `CoberturaDiff.diff_total_misses(class_name=None)` > `CoberturaDiff.diff_total_misses(filename=None)`
    - `CoberturaDiff.diff_total_hits(class_name=None)` > `CoberturaDiff.diff_total_hits(filename=None)`
    - `CoberturaDiff.diff_line_rate(class_name=None)` > `CoberturaDiff.diff_line_rate(filename=None)`
    - `CoberturaDiff.diff_missed_lines(class_name)` > `CoberturaDiff.diff_missed_lines(filename)`
    - `CoberturaDiff.classes()` > `CoberturaDiff.files()`
    - `CoberturaDiff.class_source(class_name)` > `CoberturaDiff.file_source(filename)`
    - `CoberturaDiff.class_source_hunks(class_name)` > `CoberturaDiff.file_source_hunks(filename)`
    - `Reporter.get_source(class_name)` > `Reporter.get_source(filename)`
    - `HtmlReporter.get_class_row(class_name)` > `HtmlReporter.get_class_row(filename)`
    - `DeltaReporter.get_source_hunks(class_name)` > `DeltaReporter.get_source_hunks(filename)`
    - `DeltaReporter.get_class_row(class_name)` > `DeltaReporter.get_file_row(filename)`

## 0.8.0 (2015-09-28)

* *BACKWARDS INCOMPATIBLE*: return different exit codes depending on `diff`
  status. Thanks Marc Abramowitz.

## 0.7.3 (2015-07-23)

* a non-zero exit code will be returned if not all changes have been covered. If
  `--no-source` is provided then it will only check if coverage has worsened,
  which is less strict.

## 0.7.2 (2015-05-29)

* memoize expensive methods of `Cobertura` (lxml/disk)
* assume source code is UTF-8

## 0.7.1 (2015-04-20)

* prevent misalignment of source code and line numbers, this would happen when
  the source is too long causing it to wrap around.

## 0.7.0 (2015-04-17)

* pycobertura diff now renders colors in terminal with Python 2.x (worked for
  Python 3.x). For this to work we need to require Click 4.0 so that the color
  auto-detection of Click can be overridden (not possible in Click 3.0)
* Introduce `Line` namedtuple object which represents a line of source code and
  coverage status.
* *BACKWARDS INCOMPATIBLE*: List of tuples generated or handled by various
  function now return `Line` objects (namedtuple) for each line.
* add plus sign (+) in front of lines that were added/modified on HTML diff
  report
* upgrade to Skeleton 2.0.4 (88f03612b05f093e3f235ced77cf89d3a8fcf846)
* add legend to HTML diff report

## 0.6.0 (2015-02-03)

* expose `CoberturaDiff` under the pycobertura namespace
* pycobertura diff no longer reports unchanged classes

## 0.5.2 (2015-01-13)

* fix incorrect "TOTAL" row counts of the diff command when classes were added
  or removed from the second report.

## 0.5.1 (2015-01-08)

* Options of pycobertura diff `--missed` and `--no-missed` have been renamed to
  `--source` and `--no-source` which will not show the source code nor display
  missing lines since they cannot be accurately computed without the source.
* Optimized xpath syntax for faster class name lookup (~3x)
* Colorize total missed statements
* `pycobertura diff` exit code will be non-zero until all changes are covered

## 0.5.0 (2015-01-07)

* `pycobertura diff` HTML output now only includes hunks of lines that have
  coverage changes and skips unchanged classes
* handle asymmetric presence of classes in the reports (regression introduced in
  0.4.0)
* introduce `CoberturaDiff.diff_missed_lines()`
* introduce `CoberturaDiff.classes()`
* introduce `CoberturaDiff.filename()`
* introduce `Cobertura.filepath()` which will return the system path to the
  file. It uses `base_path` to resolve the path.
* the summary table of `pycobertura diff` no longer shows classes that are no
  longer present
* `Cobertura.filename()` now only returns the filename of the class as found in
  the Cobertura report, any `base_path` computation is omitted.
* Argument `xml_source` of `Cobertura.__init__()` is renamed to `xml_path` and
  only accepts an XML path because much of the logic involved in source code
  path resolution is based on the path provided which cannot work with file
  objects or XML strings.
* Rename `Cobertura.source` -> `Cobertura.xml_path`
* `pycobertura diff` now takes options `--missed` (default) or `--no-missed` to
  show missed line numbers. If `--missed` is given, the paths to the source code
  must be accessible.

## 0.4.1 (2015-01-05)

* return non-zero exit code if uncovered lines rises (previously based on line
  rate)

## 0.4.0 (2015-01-04)

* rename `Cobertura.total_lines()` -> `Cobertura.total_statements()`
* rename `Cobertura.line_hits()` -> `Cobertura.hit_statements()`
* introduce `Cobertura.missed_statements()`
* introduce `Cobertura.line_statuses()` which returns line numbers for a given
  class name with hit/miss statuses
* introduce `Cobertura.class_source()` which returns the source code for a given
  class along with hit/miss status
* `pycobertura show` now includes HTML source
* `pycobertura show` now accepts `--source` which indicates where the source
  code directory is located
* `Cobertura()` now takes an optional `base_path` argument which will be used to
  resolve the path to the source code by joining the `base_path` value to the
  path found in the Cobertura report.
* an error is now raised if `Cobertura` is passed a non-existent XML file path
* `pycobertura diff` now includes HTML source
* `pycobertura diff` now accepts `--source1` and `--source2` which indicates
  where the source code directory of each of the Cobertura reports are located
* introduce `CoberturaDiff` used to diff `Cobertura` objects
* argument `class_name` for `Cobertura.total_statements` is now optional
* argument `class_name` for `Cobertura.total_misses` is now optional
* argument `class_name` for `Cobertura.total_hits` is now optional

## 0.3.0 (2014-12-23)

* update description of pycobertura
* pep8-ify
* add pep8 tasks for tox and travis
* diff command returns non-zero exit code if coverage worsened
* `Cobertura.branch_rate` is now a method that can take an optional `class_name`
  argument
* refactor internals for improved readability
* show classes that contain no lines, e.g. `__init__.py`
* add `Cobertura.filename(class_name)` to retrieve the filename of a class
* fix erroneous reporting of missing lines which was equal to the number of
  missed statements (wrong because of multiline statements)

## 0.2.1 (2014-12-10)

* fix py26 compatibility by switching the XML parser to `lxml` which has a more
  predictible behavior when used across all Python versions.
* add Travis CI

## 0.2.0 (2014-12-10)

* apply Skeleton 2.0 theme to html output
* add `-o` / `--output` option to write reports to a file.
* known issue: diffing 2 files with options `--format text`, `--color` and
  `--output` does not render color under PY2.

## 0.1.0 (2014-12-03)

* add `--color` and `--no-color` options to `pycobertura diff`.
* add option `-f` and `--format` with output of `text` (default) and `html`.
* change class naming from `report` to `reporter`

## 0.0.2 (2014-11-27)

* MIT license
* use pypandoc to convert the `long_description` in setup.py from Markdown to
  reStructuredText so pypi can digest and format the pycobertura page properly.

## 0.0.1 (2014-11-24)

* Initial version
