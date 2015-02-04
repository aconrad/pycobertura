# pycobertura

A Cobertura coverage parser that can diff reports and show coverage progress.

[![Travis](http://img.shields.io/travis/SurveyMonkey/pycobertura.svg?style=flat)](https://travis-ci.org/SurveyMonkey/pycobertura)
[![PyPI](http://img.shields.io/pypi/v/pycobertura.svg?style=flat)](https://pypi.python.org/pypi/pycobertura)

* [About](#about)
* [Install](#install)
* [CLI usage](#cli-usage)
* [Library usage](#library-usage)
* [How to contribute?](#how-to-contribute)
* [FAQ](#faq)

## About

pycobertura is a generic [Cobertura](http://cobertura.github.io/cobertura/)
report parser. It was also designed to help prevent code coverage from
decreasing with the `pycobertura diff` command: any line changed should be
tested and uncovered changes should be clearly visible without letting legacy
uncovered code get in the way so developers can focus solely on their changes.

Features:

* show coverage summary of a cobertura file
* output in plain text or HTML
* compare two cobertura files and show changes in coverage
* colorized diff output
* diff exit status of non-zero if coverage worsened
* fail based on uncovered lines rather than on decrease of coverage rate
  ([see why](#why-is-the-number-of-uncovered-lines-used-as-the-metric-to-check-if-code-coverage-worsened-rather-than-the-line-rate))

NOTE: The API is unstable any may be subject to changes until it reaches 1.0.

## Install

```
$ pip install pycobertura
```

## CLI usage

pycobertura provides a command line interface to report on coverage files.

### Help commands

Different help screens are available depending on what you need help about.

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

The following is a screenshot of the HTML version of another coverage file
which also include the source code with highlighted source code to indicate
whether lines were covered (green) or not (red).

```
pycobertura show --format html --output coverage.html coverage.xml
```

![](http://i.imgur.com/BYnXmAp.png)

### Command `diff`

You can also use the `diff` command to show the difference between two coverage
files. To properly compute the `Missing` column, it is necessary to provide the
source code that was used to generate each of the passed Cobertura reports
([see why](#why-do-i-need-to-provide-the-path-to-the-source-code-directory)).

```
$ pycobertura diff coverage.old.xml coverage.new.xml --source1 old_source/ --source2 new_source/
Name          Stmts    Miss    Cover     Missing
------------  -------  ------  --------  ---------
dummy/dummy   -        -2      +50.00%   -2, -5
dummy/dummy2  +2       -       +100.00%
TOTAL         +2       -2      +50.00%
```

The column `Missing` will show line numbers prefixed with either a plus sign
`+` or a minus sign `-`. When prefixed with a plus sign, the line was
introduced as uncovered and is shown in red, when prefixed as a minus sign, the
line is no longer uncovered and is rendered in green.

This screenshot shows how the HTML output only applies coverage highlighting to
the parts of the code where the coverage has changed (from covered to
uncovered, or vice versa).

```
pycobertura diff --format html --output coverage.html ./master/coverage.xml ./myfeature/coverage.xml
```

![](http://i.imgur.com/EKcdAmi.png)

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

## How to contribute?

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
pycobertura was heavily inspired by it. Both tools have similar end-goals
indeed but each tool takes a different approach to how they work.

Diff-cover uses the underlying git repository to find of lines of code that
have changed (basically `git diff`) and then looks at the Cobertura report to
check whether the lines in the diff are covered or not. The drawback of this
approach is that if the changes introduced a coverage drop elsewhere in the
code base (e.g. a legacy function no longer being called) then it can be very
hard to hunt down *where* the coverage dropped, especially if there are already
a lot of legacy uncovered lines in the mix.

On the other hand, pycobertura takes two different Cobertura reports in their
entirety and compares them line by line. If the coverage status of a line
changed from covered to uncovered or vice versa, then pycobertura will report
it regardless of where your code changes happened. Actually, sometimes you have
no code changes at all, the only changes were to add more tests and pycobertura
will show you the progress.

Moreover, pycobertura was also designed as a general purpose Cobertura parser
and can generate a summary table for a single Cobertura file (the `show`
command).

### I only have one Cobertura report and I just want to see my uncovered changes, can I do this?

Yes, this is what [diff-cover](https://github.com/edx/diff-cover) already
offers and you can achieve the same result with pycobertura. All you have to do
is pass your same coverage report twice and provide the path to the two
different code bases:

```bash
pycobertura diff coverage.xml coverage.xml --source1 master/ --source2 myfeature/
```

But keep in mind that this will not show you if your changes have introduced a
drop in coverage elsewhere in the code base. See the previous question about
the drawbacks of diff-cover.

### Why doesn't pycobertura use git to diff the source given revision SHAs rather than passing paths to the source code?

Because we would have to support N version control systems (VCS). It is easy
enough to generate a directory that contains the source code at a given commit
or branch name that it's not a top priority for pycobertura to be VCS-aware:

```bash
git archive --prefix=source1/ ${BRANCH_OR_COMMIT1} | tar -xf -
git archive --prefix=source2/ ${BRANCH_OR_COMMIT2} | tar -xf -
pycobertura diff --source1 source1/ --source2 source2/ coverage1.xml coverage2.xml -o output.html
rm -rf source1/ source2/
```

Mercurial has `hg archive` and Subversion has `svn export`. These are simple
pre-steps to running `pycobertura diff`.

Also, the code repository may not always be available at the time pycobertura
is run. Typically, in Continous Delivery pipelines, only
[artifacts](http://en.wikipedia.org/wiki/Artifact_%28software_development%29)
are available.

### Why do I need to provide the path to the source code directory?

With the command `pycobertura show`, you don't need to provide the source code
directory, unless you want the HTML output which will conveniently render the
highlighted source code for you.

But with `pycobertura diff`, if you care about *which* lines are covered or
uncovered (and not just a global count), then you will need to provide the
source for *each* of the reports.

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

How can you tell which lines need to be highlighted? Naively, you'd assume that
lines 4-5 were added and these should be the highlighted lines, the ones part
of your coverage diff. Well, that doesn't quite work.

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

The code change are lines 1-3 and these are the ones you want to highlight.
Lines 4-5 don't need to be highlighted (unless coverage status changed
in-between).

So, to accurately highlight the lines that have changed, the coverage reports
alone are not sufficient and this is why you need to provide the path to the
source that was used to generate each of the Cobertura reports and diff them to
see which lines actually changed to report accurate coverage.

### When should I use pycobertura?

pycobertura was built as a tool to educate developers about the testing culture
in such way that any code change should have one or more tests along with it.

You can use pycobertura in your Continous Integration (CI) or Continous
Delivery (CD) pipeline which would fail a build if the code changes worsened
the coverage. For example, when a pull request is submitted, the new code
should have equal or better coverage than the branch it's going to be merged
into. Or if code navigates through a release pipeline and the new code has
worse coverage than what's already in Production, then the release is aborted.

When a build is triggered by your CI/CD pipeline, each testing stage would
typically store an
[artifact](http://en.wikipedia.org/wiki/Artifact_%28software_development%29) of
the source code and another one of the Cobertura report. An extra stage in the
pipeline could ensure that the coverage did not worsen. This can be done by
retrieving the artifacts of the current build as well as the "target" artifacts
(code and Cobertura report of Production or target branch of a pull request).
Then `pycobertura diff` will take care of failing the build if the coverage
worsened (return a non-zero exit code) and then the pycobertura report can be
published as an artifact to make it available to developers to look at.

The step could look like this:

```bash
# Download artifacts of current build
curl -o coverage.${BUILD_ID}.xml https://ciserver/artifacts/${BUILD_ID}/coverage.xml
curl -o source.${BUILD_ID}.zip https://ciserver/artifacts/${BUILD_ID}/source.zip

# Download artifacts of already-in-Prod build
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
of our code, we legitimately delete a covered line and the following coverage
report is generated:

```
line 1: hit
### line deleted ###
line 2: miss
line 3: hit
line 4: hit
```

The line rate decreased from 80% to 75% but uncovered lines is still at 1. In
this case, failing the build based on line rate would is inappropriate, thus
making the line rate the wrong metric to look at when validating coverage.

The basic idea is that a code base may have technical debt of N uncovered lines
and you want to prevent N from ever going up.

### pycobertura sounds cool, but how to I generate a Cobertura file?

Depending on your programing language, you need to find a tool that measures
code coverage and generates a Cobertura report which is an XML representation
of your code coverage results.

In Python, [coverage.py](http://nedbatchelder.com/code/coverage/) is a great
tool for measuring code coverage and plugins such as
[pytest-cov](https://pypi.python.org/pypi/pytest-cov) for
[pytest](http://pytest.org/latest/) and
[nosexcover](https://pypi.python.org/pypi/nosexcover) for
[nose](https://nose.readthedocs.org/en/latest/) are available to generate
Cobertura reports while running tests.

Cobertura is a very common file format available in many testing tools for
pretty much all programing languages. pycobertura is language agnostic and
should work with reports generated by tools in any language. But it was mostly
developped and tested against reports generated with the `pytest-cov` plugin in
Python. If you see issues, please [create a
ticket](https://github.com/SurveyMonkey/pycobertura/issues).
