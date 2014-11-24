# pycobertura

A Cobertura coverage report parser written in Python.

## CLI usage

pycobertura provides a command line interface to report on coverage files:

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

You can also use the `diff` command to show the difference between two coverage
files:

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

from pycobertura import TextReport
tr = TextReport(cobertura)
tr.generate() == """\
Name                     Stmts    Miss  Cover    Missing
---------------------  -------  ------  -------  ---------
pycobertura/__init__         1       0  100.00%
pycobertura/cli             18       0  100.00%
pycobertura/cobertura       93       0  100.00%
pycobertura/reports        129       0  100.00%
pycobertura/utils           12       0  100.00%
TOTAL                      253       0  100.00%"""

from pycobertura import TextReportDelta

coverage1 = Cobertura('coverage1.xml')
coverage2 = Cobertura('coverage2.xml')
delta = TextReportDelta(coverage1, coverage2)
delta.generate() == """\
Name          Stmts    Miss    Cover     Missing
------------  -------  ------  --------  ---------
dummy/dummy   -        -2      +50.00%   -2, -5
dummy/dummy2  +2       -       +100.00%
TOTAL         +2       -2      +50.00%"""
```
