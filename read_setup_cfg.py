import os
from setuptools.config import read_configuration

if __name__=="__main__":
    conf_dict = read_configuration("setup.cfg")

    pkg_name= conf_dict['metadata']['name']
    pkg_version = conf_dict['metadata']['version']

    print(pkg_name)
    print(pkg_version)