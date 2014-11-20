# Generating custom coverage for testing purpose

The `dummy/` directory contains a Python application with tests that was
created for the purpose of generating coverage files (using coverage.py). You
can tweak the tests and the dummy code in order to have pytest generate
different coverage reports that can be used as part of the tests for
pycobertura.

# Running tests for the dummy app

To run the tests for dummy, cd into the directory and simply run pytest.

```
$ cd dummy/
$ py.test
```

Save the generated `coverage.xml` file under the filename
`dummy.<something-meaningful-about-this-coverage>.xml` and move it in the
directory of the pycobertura tests. You can then start writing tests cases for
pycobertura using the new coverage file.
