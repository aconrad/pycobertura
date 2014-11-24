# Before you release
# - bump package version in setup.py
# - update the package version in the CHANGES file

PKG_NAME=$(python setup.py --name)
PKG_VERSION=$(python setup.py --version)

git tag -am "release v${PKG_VERSION}" v${PKG_VERSION}
git push --tags
python setup.py sdist upload -r https://pypi.python.org/pypi
