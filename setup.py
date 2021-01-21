import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version = '2.0.1'

try:
    import pypandoc
    README = pypandoc.convert_file('README.md', 'rst')
    CHANGES = pypandoc.convert_file('CHANGES.md', 'rst')
except:
    README = read('README.md')
    CHANGES = read('CHANGES.md')

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
    long_description='%s\n\n%s' % (README, CHANGES),
    setup_requires=['setuptools_git'],
    install_requires=['click>=4.0', 'jinja2', 'lxml', 'tabulate'],
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
    entry_points={
        'console_scripts': [
            'pycobertura=pycobertura.cli:pycobertura'
        ],
    },
)
