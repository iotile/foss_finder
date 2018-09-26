from foss_finder.config.config import DEFAULT_COLUMNS
from foss_finder.config.strings import OVERWRITES_NAME

from .field import UserDefinedInformationField


class Overwrites(UserDefinedInformationField):
    """
    Implements a field of the user-defined information file.
    This field's purpose is to overwrite information about a dependency.
    In other words, modify the information given by foss_finder because it is incorrect.
    """
    NAME = OVERWRITES_NAME

    def _transform_row(self, row, package_info):
        assert len(row) == len(DEFAULT_COLUMNS)
        res = row.copy()
        for column, value in package_info.items():
            res[DEFAULT_COLUMNS.index(column)] = value
        return res
