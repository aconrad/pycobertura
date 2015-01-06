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
what is left to test. This ensures that any code change is tested moving
forward without letting legacy uncovered lines get in your way, allowing
developers to focus solely on their changes.

## Screenshots

### pycobertura show

The following screenshot is the result of the command `pycobertura show` which
will render a summary table (like the text version) but also include the source
code with lines highlighted in green or green to indicate whether lines were
covered (green) and not (red).

```
pycobertura show --format html --output coverage.html coverage.xml
```

![pycobertura show screenshot](http://i.imgur.com/sC6iIuB.png)

### pycobertura diff

This screenshot is a sample HTML output of the command `pycobertura diff` which
only applies coverage highlighting to the parts of the code where the coverage
has changed (from covered to uncovered, or vice versa).

```
pycobertura diff --format html --output coverage.html coverage.old.xml coverage.new.xml
```

![pycobertura diff screenshot](http://i.imgur.com/5xkrUwO.png)

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

Found a bug/typo? Got a patch? Have an idea? Please use Github issues or fork
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

## FAQ

### Isn't pycobertura the same tool as diff-cover?

[Diff-cover](https://github.com/edx/diff-cover) is a fantastic tool and
pycobertura was heavily inspired by it. Diff-cover uses the underlying git
repository to find of lines of code that have changed (basically `git diff`)
and then looks at the Cobertura report to check whether the lines in the diff
are covered or not. The drawback of this approach is that if the changes
introduced a coverage drop elsewhere in the code base (e.g. a legacy function
no longer being called) then it can be very hard to hunt down *where* the
coverage dropped, especially if there is already a lot of legacy uncovered
lines in the mix.

On the other hand, pycobertura takes two different Cobertura reports in their
entirety and compares them line by line. If the coverage status of a line
changed from covered to uncovered or vice versa, then pycobertura will report
it regardless of where your code changes happened. Actually, sometimes you have
no code changes at all, the only change is to add more tests and pycobertura
will show you the progress.

Moreover, pycobertura was also designed as a general purpose Cobertura parser.

### Why do I need to provide the path to the source code directory?

With the command `pycobertura show`, you don't really to provide the source
code directory, unless you want the HTML output which will conveniently render
the highlithed source code for you.

But with `pycobertura diff`, if you care about *which* lines are
covered/uncovered (and not just a global count), then to properly report these
lines you will need to provide the source for *each* of the reports.

To better understand why, let's assume we have 2 Cobertura reports with the
following info:

Report A:

```
line 1, hit
line 2, miss
line 3, hit
```

and Report B:

```
line 1, hit
line 2, miss
line 3, hit
line 4, miss
line 5, hit
```

How can you tell which line increased or decreased in coverage? Naively, you'd
assume that lines 4-5 were added and these should be the highlighted lines, the
ones part of your coverage diff. Well, that doesn't quite work.

The code for Report A is:

```python
if foo is True:  # line 1
    total += 1   # line 2
return total     # line 3
```

The code for Report B is:

```python
if foo is False:   # line 1  # new line
    total -= 1     # line 2  # new line
elif foo is True:  # line 3  # modified line
    total += 1     # line 4, unchanged
return total       # line 5, unchanged
```

The code change was lines 1-3 and these are the ones you want to highlight with
coverage info. Line 4-5 don't need to be highlighted (unless coverage status
changed in-between).

So, to accurately highlight the lines that have changed, the coverage reports
alone are not sufficient and this is why you need to provide the path to the
source that was used to generate each of the Cobertura reports and diff them to
see which lines actually changed and report coverage info.

### When should I use pycobertura?

pycobertura was built as a tool to educate developers about the testing culture
in such way that any code change should have a test along with it.

You can use pycobertura in your Continous Integration (CI) or Continous
Delivery (CD) pipeline which would fail a build if the code changes worsened
the coverage. For example, when a pull request is submitted, the new code
should have equal or better coverage than the branch it's going to be merged
into. Or if code navigates through a release pipeline and the new code has
worse coverage than what's already in Production, then the release is aborted.

When a build is triggered by your CI/CD pipeline, each build would typically
store as artifacts the source code and the Cobertura report for it. An extra
stage in the pipeline could ensure that the coverage did not go down. This can
be done by retrieving the artifacts of the current build as well as the
"target" artifacts (code and Cobertura report of Production or target branch of
a pull request). Then `pycobertura diff` will take care of failing the build if
the coverage worsened (return a non-zero exit code) and submit the pycobertura
report as an artifact (e.g., the HTML output) and make this report available
for developers to look at.

The step could look like this:

```bash
# Download artifacts of current build
curl -o coverage.${BUILD_ID}.xml https://ciserver/artifacts/${BUILD_ID}/coverage.xml
curl -o source.${BUILD_ID}.zip https://ciserver/artifacts/${BUILD_ID}/source.zip

# Download artifacts of "target" build
curl -o coverage.${PROD_BUILD}.xml https://ciserver/artifacts/${PROD_BUILD}/coverage.xml
curl -o source.${PROD_BUILD}.zip https://ciserver/artifacts/${PROD_BUILD}/source.zip

unzip source.${BUILD_ID}.zip -d source.${BUILD_ID}
unzip source.${PROD_BUILD}.zip -d source.${PROD_BUILD}

# Compare
pycobertura diff --format html \
                 --output pycobertura-diff.${BUILD_ID}.html \
                 --source1 source.${PROD_BUILD} \
                 --source2 source.${BUILD_ID} \
                 coverage.${PROD_BUILD}.xml \
                 coverage.${BUILD_ID}.xml

# Upload the pycobertura report artifact
curl -F filedata=@pycobertura-diff.${BUILD_ID}.html http://ciserver/artifacts/${BUILD_ID}/
```

### Why is the number of uncovered lines used as the metric to check if code coverage worsened rather than the line rate?

The line rate (percentage of covered lines) can legitimately go down for a
number of reasons. To illustrate, suppose we have this code coverage report for
version A of our code:

```
line 1: hit
line 2: hit
line 3: miss
line 4: hit
line 5: hit
```

Here, the line rate is 80% and uncovered lines is 1 (miss). Later in version B
of our code, the following coverage report is generated:

```
line 1: hit
### line deleted ###
line 2: miss
line 3: hit
line 4: hit
```

Now the line rate is 75% and uncovered lines is still 1. In this case, failing
the build based on line rate would be inappropriate, thus making the line rate
the wrong metric to fail a build.

The basic idea is that a code base may have technical debt of N uncovered lines
and you want to prevent N from ever going up.
