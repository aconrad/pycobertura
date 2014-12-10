# Release Notes

## Unreleased

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
* use pypandoc to convert the `long_description` in setup.py from Markdown to reStructuredText so pypi can digest and format the pycobertura page properly.

## 0.0.1 (2014-11-24)

* Initial version
