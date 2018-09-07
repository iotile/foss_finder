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
USE_SEMVER = ini_config['NPM parser'].getboolean('use_semver')
NPM_SECTIONS = {
    PRODUCTION: ini_config['NPM sections']['npm_prod'].replace(',', '').split('\n'),
    DEVELOPMENT: ini_config['NPM sections']['npm_dev'].replace(',', '').split('\n'),
}
PYTHON_FILES = {
    PRODUCTION: ini_config['Python files']['py_prod'].replace(',', '').split('\n'),
    DEVELOPMENT: ini_config['Python files']['py_dev'].replace(',', '').split('\n'),
}
IGNORED_REPOS = ini_config['Ignored repositories']['ignored_repos'].replace(',', '').split('\n')
