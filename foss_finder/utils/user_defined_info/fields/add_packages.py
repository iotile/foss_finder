from foss_finder.config.strings import *
from foss_finder.config.config import DEFAULT_COLUMNS

from .field import UserDefinedInformationField


class AddPackages(UserDefinedInformationField):
    """
    Implements a field of the user-defined information file.
    This field's purpose is to add dependencies to a project.
    In other words, add information about packages that could not be found by foss_finder.
    """
    NAME = ADD_PACKAGE_NAME

    def __init__(self, local_data=[], global_data=[], *args, **kwargs):
        super(AddPackages, self).__init__(local_data=local_data, global_data=global_data, *args, **kwargs)
        self._package_info_useless_keys = (OWNER, REASON)

    def _transform_row(self, row, package_info):
        assert len(row) == len(DEFAULT_COLUMNS)
        res = row.copy()
        for col, val in package_info.items():
            res[DEFAULT_COLUMNS.index(col)] = val
        return res
