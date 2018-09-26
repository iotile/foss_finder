from .field import UserDefinedInformationField

from .config import OVERWRITES_NAME, DEFAULT_COLUMNS

class Overwrites(UserDefinedInformationField):
    NAME = OVERWRITES_NAME

    def _transform_row(self, row, package_info):
        assert len(row) == len(DEFAULT_COLUMNS)
        res = row.copy()
        for column, value in package_info.items():
            res[DEFAULT_COLUMNS.index(column)] = value
        return res
