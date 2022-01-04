import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version = '2.1.0'

# According to https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/ .md is supported 
# -> no pypandoc needed anymore to generate reStructuredText

long_description = read('README.md') + '\n' + read('CHANGES.md') + '\n'

setup(
    name="pycobertura",
    version=version,
    author="Alex Conrad",
    author_email="alexandre.conrad@gmail.com",
    maintainer="Alex Conrad",
    maintainer_email="alexandre.conrad@gmail.com",
    description="A Cobertura coverage parser that can diff reports and "
                "show coverage progress.",
    license="MIT License",
    keywords="cobertura coverage diff report parser parse xml",
    url="https://github.com/aconrad/pycobertura",
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=['tests']),
    long_description=long_description,
    long_description_content_type='text/markdown',
    setup_requires=['setuptools_git'],
    install_requires=['click>=4.0', 'jinja2', 'lxml', 'tabulate'],
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3"
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        'console_scripts': [
            'pycobertura=pycobertura.cli:pycobertura'
        ],
    },
)
