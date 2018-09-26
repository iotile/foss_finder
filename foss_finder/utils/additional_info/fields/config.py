from config.strings import *
from config import config

# default columns of the csv
DEFAULT_COLUMNS = config.FIELDS
# optional columns added to the csv by the user
OPTIONAL_COLUMNS = ['linkage', 'justification', 'usage']

# names of the fields
ADD_PACKAGE_NAME = 'add-packages'
OVERWRITES_NAME = 'overwrites'
MULTI_LICENSE_SELECTION_NAME = 'multi-license-selection'
ADDITIONAL_INFO_NAME = 'additional-info'

# fields of the user-defined information file with their required and optional attributes
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
