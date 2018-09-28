import configparser

from .strings import *


###############################################################
# First, define variables by using the INI configuration file #
###############################################################

# Path of the INI configuration file (relative to the root of foss_finder)
INI_PATH = '.foss_finder'

# Processing of the INI configuration file
ini_config = configparser.ConfigParser()
ini_config.read(INI_PATH)

# Exposed variables
if 'User defined information' in ini_config:
    OPTIONAL_COLUMNS = ini_config['User defined information']['optional_columns'].replace(',', '').split('\n')
else:
    OPTIONAL_COLUMNS = []

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
    NPM_SECTIONS = {
        PRODUCTION: [],
        DEVELOPMENT: [],
    }

if 'Python files' in ini_config:
    PYTHON_FILES = {
        PRODUCTION: ini_config['Python files']['py_prod'].replace(',', '').split('\n'),
        DEVELOPMENT: ini_config['Python files']['py_dev'].replace(',', '').split('\n'),
    }
else:
    PYTHON_FILES = {
        PRODUCTION: [],
        DEVELOPMENT: [],
    }

if 'Ignored repositories' in ini_config:
    IGNORED_REPOS = ini_config['Ignored repositories']['ignored_repos'].replace(',', '').split('\n')
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
