# pycobertura

A [Cobertura](http://cobertura.github.io/cobertura/) coverage parser that can
diff reports.

![Travis](http://img.shields.io/travis/SurveyMonkey/pycobertura.svg?style=flat)
![PyPI](http://img.shields.io/pypi/v/pycobertura.svg?style=flat)

Features:

* show coverage summary of a cobertura file
* compare two cobertura files and show changes
* output in plain text or HTML
* colorized diff output
* diff exit status of non-zero if number of uncovered lines rose

pycobertura was designed for people who want to prevent their code coverage
from decreasing. Any line changed should be tested and newly introduced code
that is uncovered should fail a build and clearly show the author of the change
what is left to test.

Typically, Continous Integration (CI) or Continous Delivery (CD) tools would
want to test new code and compare it with the previous successful build (e.g.,
production or the target branch of a pull request) whether the number of
uncovered lines rose and if it did, fail the build. This ensures that any code
change is tested moving forward without letting legacy uncovered lines get in
your way, allowing developers to focus solely on their changes.

## Install

```
$ pip install pycobertura
```

## CLI usage

pycobertura provides a command line interface to report on coverage files.

### Help commands

```
$ pycobertura --help
$ pycobertura show --help
$ pycobertura diff --help
```

### Command `show`

The `show` command displays the report summary of a coverage file.

```
$ pycobertura show coverage.xml
Name                     Stmts    Miss  Cover    Missing
---------------------  -------  ------  -------  ---------
pycobertura/__init__         1       0  100.00%
pycobertura/cli             18       0  100.00%
pycobertura/cobertura       93       0  100.00%
pycobertura/reports        129       0  100.00%
pycobertura/utils           12       0  100.00%
TOTAL                      253       0  100.00%
```

### Command `diff`

You can also use the `diff` command to show the difference between two coverage
files.

```
$ pycobertura diff coverage.old.xml coverage.new.xml
Name          Stmts    Miss    Cover     Missing
------------  -------  ------  --------  ---------
dummy/dummy   -        -2      +50.00%   -2, -5
dummy/dummy2  +2       -       +100.00%
TOTAL         +2       -2      +50.00%
```

The column `Missing` will show line numbers prefixed with either a plus sign
`+` or a minus sign `-`. When prefixed with a plus sign, the line was
introduced as uncovered, when prefixed as a minus sign, the line is no longer
uncovered.

## Library usage

Using it as a library in your Python application is easy:

```python
from pycobertura import Cobertura
cobertura = Cobertura('coverage.xml')

cobertura.version == '3.7.1'
cobertura.line_rate() == 1.0  # 100%
cobertura.classes() == [
    'pycobertura/__init__',
    'pycobertura/cli',
    'pycobertura/cobertura',
    'pycobertura/reports',
    'pycobertura/utils',
]
cobertura.line_rate('pycobertura/cli') == 1.0

from pycobertura import TextReporter
tr = TextReporter(cobertura)
tr.generate() == """\
Name                     Stmts    Miss  Cover    Missing
---------------------  -------  ------  -------  ---------
pycobertura/__init__         1       0  100.00%
pycobertura/cli             18       0  100.00%
pycobertura/cobertura       93       0  100.00%
pycobertura/reports        129       0  100.00%
pycobertura/utils           12       0  100.00%
TOTAL                      253       0  100.00%"""

from pycobertura import TextReporterDelta

coverage1 = Cobertura('coverage1.xml')
coverage2 = Cobertura('coverage2.xml')
delta = TextReporterDelta(coverage1, coverage2)
delta.generate() == """\
Name          Stmts    Miss    Cover     Missing
------------  -------  ------  --------  ---------
dummy/dummy   -        -2      +50.00%   -2, -5
dummy/dummy2  +2       -       +100.00%
TOTAL         +2       -2      +50.00%"""
```

## Contribute

Found a bug? Got a patch? Have an idea? Please use Github issues or fork
pycobertura and submit a pull request (PR). All contributions are welcome!

If you submit a PR:

* ensure the description of your PR illustrates your changes clearly by showing
  what the problem was and how you fixed it (before/after)
* make sure your changes are covered with one or more tests
* add a descriptive note in the CHANGES file under the `Unreleased` section
* update the README accordingly if your changes outdate the documentation
* make sure all tests are passing using `tox`

```
pip install tox
tox
```
