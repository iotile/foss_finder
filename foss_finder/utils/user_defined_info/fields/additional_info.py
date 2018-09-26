from config.config import DEFAULT_COLUMNS, OPTIONAL_COLUMNS
from config.strings import ADDITIONAL_INFO_NAME

from .field import UserDefinedInformationField


class AdditionalInfo(UserDefinedInformationField):
    NAME = ADDITIONAL_INFO_NAME

    def _transform_row(self, row, package_info):
        initial_row_length = len(DEFAULT_COLUMNS) + 1
        assert len(row) == initial_row_length + len(OPTIONAL_COLUMNS)
        res = row.copy()
        for column, value in package_info.items():
            res[initial_row_length + OPTIONAL_COLUMNS.index(column)] = value
        return res
