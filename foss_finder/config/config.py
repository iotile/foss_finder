import configparser

from .strings import * 

# Fields of the CSV files (ordered)
FIELDS = [
    REGISTRY,
    PACKAGE,
    LICENSE,
    VERSION,
    URL,
]

# Path of the INI configuration file (relative to the root of foss_finder)
INI_PATH = '.foss_finder'

# Processing of the INI configuration file
ini_config = configparser.ConfigParser()
ini_config.read(INI_PATH)
# Exposed variables
if 'NPM parser' in ini_config:
    USE_SEMVER = ini_config['NPM parser'].getboolean('use_semver')
else:
    USE_SEMVER = False

if 'NPM sections' in ini_config:
    NPM_SECTIONS = {
        PRODUCTION: ini_config['NPM sections']['npm_prod'].replace(',', '').split('\n'),
        DEVELOPMENT: ini_config['NPM sections']['npm_dev'].replace(',', '').split('\n'),
    }
else:
    NPM_SECTIONS = {}

if 'Python files' in ini_config:
    PYTHON_FILES = {
        PRODUCTION: ini_config['Python files']['py_prod'].replace(',', '').split('\n'),
        DEVELOPMENT: ini_config['Python files']['py_dev'].replace(',', '').split('\n'),
    }
else:
    PYTHON_FILES = {}

if 'Ignored repositories' in ini_config:
    IGNORED_REPOS = ini_config['Ignored repositories']['ignored_repos'].replace(',', '').split('\n')
