import os
import sys
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version = '0.0.1'

setup(
    name="pycobertura",
    version=version,
    author="Alex Conrad",
    author_email="alexandre@surveymonkey.com",
    maintainer="Alex Conrad",
    maintainer_email="alexandre@surveymonkey.com",
    description="A Cobertura coverage report parser written in Python.",
    license="SurveyMonkey. All Rights Reserved.",
    keywords="cobertura coverage parser parse xml",
    url="http://code.corp.surveymonkey.com/devmonkeys/smjenkins",
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=['tests']),
    long_description=read('README.md'),
    setup_requires=['setuptools_git'],
    install_requires=['click', 'tabulate'],
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    entry_points = {
        'console_scripts': [
            'pycobertura=pycobertura.cli:pycobertura'
        ],
    },
)
