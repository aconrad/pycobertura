# Before you release
# - install twine: pip install twine
# - bump package version in `__version__`
# - update the package version in the CHANGES file
# - commit the changes to master and push

PKG_NAME=pycobertura
PKG_VERSION=$(cat __version__)

git tag -am "release v${PKG_VERSION}" "v${PKG_VERSION}"
git push --tags
pip install build
python -m build
twine upload dist/"${PKG_NAME}-${PKG_VERSION}"*{.tar.gz,.whl}
