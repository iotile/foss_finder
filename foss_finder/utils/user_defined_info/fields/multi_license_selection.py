import re

from foss_finder.config.strings import *
from foss_finder.config.config import DEFAULT_COLUMNS

from .field import UserDefinedInformationField


class MultiLicenseSelection(UserDefinedInformationField):
    """
    Implements a field of the user-defined information file.
    This field's purpose is to select a license from a multi-license.
    In other words, choose the license that is used when the package is multi-licensed.
    """
    NAME = MULTI_LICENSE_SELECTION_NAME

    def __init__(self, data, *args, **kwargs):
        super(MultiLicenseSelection, self).__init__(data, *args, **kwargs)
        self._package_info_useless_keys = (OWNER, REASON)

    def _validate_multi_license_selection(self, package_info, multi_license):
        selected_license = package_info[MULTI_LICENSE_SELECTION]
        package_name = package_info[PACKAGE]
        package_version = package_info.get(VERSION)
        lower_multi_license = multi_license.lower()
        if not(' or ' in lower_multi_license or ' and ' in lower_multi_license):
            if package_version:
                msg = f'Invalid license for package {package_name} version {package_version}.'
            else:
                msg = f'Invalid license for package {package_name}.'
            msg += f' {multi_license} is not a multi-license.'
            raise ValueError(msg)
        licenses = re.split(r' or | and |\(|\)', lower_multi_license)
        if selected_license.lower() not in licenses:
            if package_version:
                msg = f'Invalid license for package {package_name} version {package_version}.'
            else:
                msg = f'Invalid license for package {package_name}.'
            msg += f' {selected_license} is not part of the following multi-license: {multi_license}.'
            raise ValueError(msg)
        return selected_license

    def _transform_row(self, row, package_info):
        assert len(row) == len(DEFAULT_COLUMNS) + 1
        res = row.copy()
        res[-1] = self._validate_multi_license_selection(package_info, row[DEFAULT_COLUMNS.index(LICENSE)])
        return res
