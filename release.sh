# Before you release
# - install twine: pip install twine
# - bump package version in setup.cfg
# - update the package version in the CHANGES file
# - commit the changes to master and push

pip install .  # installs the new version after bump so the line PKG_VERSION gets the right version

PKG_NAME=pycobertura
# from importlib import metadata is unfortunately only available from Python 3.8 onwards
PKG_VERSION=$(python -c "from pkg_resources import get_distribution; print(get_distribution('pycobertura').version)")

git tag -am "release v${PKG_VERSION}" "v${PKG_VERSION}"
git push --tags
pip install build
python -m build
twine upload dist/"${PKG_NAME}-${PKG_VERSION}"*{.tar.gz,.whl}
