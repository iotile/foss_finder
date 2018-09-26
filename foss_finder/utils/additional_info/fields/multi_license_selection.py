from .field import UserDefinedInformationField

from .config import MULTI_LICENSE_SELECTION_NAME, DEFAULT_COLUMNS

from config.strings import *


class MultiLicenseSelection(UserDefinedInformationField):
    NAME = MULTI_LICENSE_SELECTION_NAME

    def _validate_multi_license_selection(self, selected_license, multi_license):
        raise NotImplementedError

    def _transform_row(self, row, package_info):
        assert len(row) == len(DEFAULT_COLUMNS) + 1
        res = row.copy()
        selected_license = package_info[MULTI_LICENSE_SELECTION]
        self._validate_multi_license_selection(selected_license, row[DEFAULT_COLUMNS.index(LICENSE)])
        res[-1] = selected_license
        return res
