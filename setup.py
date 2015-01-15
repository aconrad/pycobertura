import os
import sys
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def get_description():
    toc, about, features, leftover = read("README.md").split("## ", 3)
    CHANGES = read('CHANGES.md')

    DESCRIPTION = """\
# pycobertura

## %s

## %s

%s""" % (
    about.strip(),
    features.strip(),
    CHANGES.replace('## Unreleased\n\n', ''))

    try:
        import pypandoc
        return pypandoc.convert(DESCRIPTION, 'rst', format='md')
    except:
        return DESCRIPTION

version = '0.5.2'

setup(
    name="pycobertura",
    version=version,
    author="Alex Conrad",
    author_email="alexandre@surveymonkey.com",
    maintainer="Alex Conrad",
    maintainer_email="alexandre@surveymonkey.com",
    description="A Cobertura coverage parser that can diff reports and show coverage progress.",
    license="MIT License",
    keywords="cobertura coverage parser parse xml",
    url="https://github.com/SurveyMonkey/pycobertura",
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=['tests']),
    long_description=get_description(),
    setup_requires=['setuptools_git'],
    install_requires=['click', 'colorama', 'jinja2', 'lxml', 'tabulate'],
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4"
    ],
    entry_points = {
        'console_scripts': [
            'pycobertura=pycobertura.cli:pycobertura'
        ],
    },
)
