# Before you release
# - install twine: pip install twine
# - bump package version in setup.cfg
# - update the package version in the CHANGES file
# - commit the changes to master and push

PKG_NAME = $(python read_setup_cfg.py | head -n1)
PKG_VERSION = $(python read_setup_cfg.py | tail -n1)

git tag -am "release v${PKG_VERSION}" "v${PKG_VERSION}"
git push --tags
python -m build
twine upload dist/"${PKG_NAME}-${PKG_VERSION}*"
