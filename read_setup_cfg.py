import configparser
import argparse

config = configparser.ConfigParser()

with open('setup.cfg') as f:
    config.read_file(f)

parser = argparse.ArgumentParser(description='Return setup.cfg section value for given metadata key')
parser.add_argument('--section', metavar='section', nargs=1, help="section header")
parser.add_argument('--key', metavar='key', nargs=1, help='metadata key')
args = vars(parser.parse_args())

section, key = args['section'], args['key']

if type(section) == list:
    section = section[0]
if type(key) == list:
    key = key[0]

print(config[section][key])