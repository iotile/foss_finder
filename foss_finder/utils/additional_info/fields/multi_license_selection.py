import re

from config.strings import *
from config.config import DEFAULT_COLUMNS

from .field import UserDefinedInformationField


class MultiLicenseSelection(UserDefinedInformationField):
    NAME = MULTI_LICENSE_SELECTION_NAME

    def _validate_multi_license_selection(self, selected_license, multi_license):
        lower_multi_license = multi_license.lower()
        if not(' or ' in lower_multi_license or ' and ' in lower_multi_license):
            raise ValueError(f'{multi_license} is not a multi-license.')
        licenses = re.split(r' or | and |\(|\)', lower_multi_license)
        if selected_license.lower() not in licenses:
            raise ValueError(f'{selected_license} is not part of the following multi-license: {multi_license}.')


    def _transform_row(self, row, package_info):
        assert len(row) == len(DEFAULT_COLUMNS) + 1
        res = row.copy()
        selected_license = package_info[MULTI_LICENSE_SELECTION]
        self._validate_multi_license_selection(selected_license, row[DEFAULT_COLUMNS.index(LICENSE)])
        res[-1] = selected_license
        return res
