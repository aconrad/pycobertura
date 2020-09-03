# Before you release
# - install pandoc on your system: apt-get install pandoc
# - install pypandoc: pip install pypandoc
# - install twine: pip install twine
# - bump package version in setup.py
# - update the package version in the CHANGES file
# - commit the changes to master and push

PKG_NAME=$(python setup.py --name)
PKG_VERSION=$(python setup.py --version)

git tag -am "release v${PKG_VERSION}" v${PKG_VERSION}
git push --tags
python setup.py sdist
twine upload dist/${PKG_NAME}-${PKG_VERSION}.tar.gz
