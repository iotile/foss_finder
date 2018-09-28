import configparser

import foss_finder.utils.validators

from .strings import *


###############################################################
# First, define variables by using the INI configuration file #
###############################################################

# Path of the INI configuration file (relative to the root of foss_finder)
INI_PATH = '.foss_finder'

# Processing of the INI configuration file
ini_config = configparser.ConfigParser()
ini_config.read(INI_PATH)

# Define function to clean data from INI configuration file
def clean(data):
    if data:
        return data.replace(',', '').split('\n')
    else:
        return []

# Exposed variables
if 'User defined information' in ini_config:
    OPTIONAL_COLUMNS = clean(ini_config['User defined information']['optional_columns'])
else:
    OPTIONAL_COLUMNS = []

if 'NPM parser' in ini_config:
    USE_SEMVER = ini_config['NPM parser'].getboolean('use_semver')
else:
    USE_SEMVER = False

if 'NPM sections' in ini_config:
    NPM_SECTIONS = {
        PRODUCTION: clean(ini_config['NPM sections']['npm_prod']),
        DEVELOPMENT: clean(ini_config['NPM sections']['npm_dev']),
    }
else:
    NPM_SECTIONS = {
        PRODUCTION: [],
        DEVELOPMENT: [],
    }

if 'Python files' in ini_config:
    PYTHON_FILES = {
        PRODUCTION: clean(ini_config['Python files']['py_prod']),
        DEVELOPMENT: clean(ini_config['Python files']['py_dev']),
    }
else:
    PYTHON_FILES = {
        PRODUCTION: [],
        DEVELOPMENT: [],
    }

if 'Checks' in ini_config:
    VALIDATORS = clean(ini_config['Checks']['validators'])
else:
    VALIDATORS = []

if 'Ignored repositories' in ini_config:
    IGNORED_REPOS = clean(ini_config['Ignored repositories']['ignored_repos'])
else:
    IGNORED_REPOS = []


############################################################################
# Now, define variables that are not related to the INI configuration file #
############################################################################

# Default columns of the CSV files (ordered)
DEFAULT_COLUMNS = [
    REGISTRY,
    PACKAGE,
    LICENSE,
    VERSION,
    URL,
]

# Name of the local user-defined information file (must be at the root of a repository)
USER_DEFINED_INFORMATION_NAME = '.foss.json'

# Name of the global user-defined information file (must be in the folder where you run the script)
GLOBAL_USER_DEFINED_INFORMATION_NAME = '.foss.global.json'

# Fields of the user-defined information file with their required and optional attributes
USER_DEFINED_INFORMATION_FIELDS = {
    ADD_PACKAGE_NAME: (
        # required
        [
            PACKAGE,
            VERSION,
            LICENSE,
            OWNER,
        ],
        # optional
        DEFAULT_COLUMNS,
    ),
    OVERWRITES_NAME: (
        # required
        [
            PACKAGE,
            OWNER,
            REASON,
        ],
        # optional
        [VERSION] + DEFAULT_COLUMNS,
    ),
    MULTI_LICENSE_SELECTION_NAME: (
        # required
        [
            PACKAGE,
            OWNER,
            MULTI_LICENSE_SELECTION,
        ],
        # optional
        [VERSION],
    ),
    ADDITIONAL_INFO_NAME: (
        # required
        [
            PACKAGE,
            OWNER,
        ],
        # optional
        [VERSION] + OPTIONAL_COLUMNS,
    ),
}

# Maps validator keys to the actual check classes

VALIDATORS_MAP = {
    GPL_CHECK: foss_finder.utils.validators.GPLCheck,
}
