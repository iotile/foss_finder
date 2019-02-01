import foss_finder.config.config
from foss_finder.config.strings import LICENSE, PACKAGE, VERSION

from .base import Check, CheckError


class MultiLicenseCheckError(CheckError):
    """
    Raised when the multi-license check doesn't pass. (The package is multi-licensed and no license has been chosen.)
    """

    def __init__(self, package_name, package_version, package_license):
        self.package_name = package_name
        self.package_version = package_version
        self.package_license = package_license
        self.message = f'Package {package_name} version {package_version} is licensed under {package_license} and no license has been chosen'


class MultiLicenseCheck(Check):
    """
    Checks that the license is not a multi-license.
    If it is, checks that one of the licenses has been chosen.
    """
    NAME = 'Multi-license Check'
    DESCRIPTION = 'Checks that there is only one chosen license from a multi-license'

    def __init__(self, *args, **kwargs):
        default_columns = foss_finder.config.config.DEFAULT_COLUMNS
        if LICENSE in default_columns and PACKAGE in default_columns and VERSION in default_columns:
            self.license_index = default_columns.index(LICENSE)
            self.name_index = default_columns.index(PACKAGE)
            self.version_index = default_columns.index(VERSION)
        else:
            raise ValueError('Package, version, and license must be in the default columns.')
        self.multi_license_selection_index = len(default_columns)

    def check(self, package_info):
        package_license = package_info[self.license_index]
        package_name = package_info[self.name_index]
        package_version = package_info[self.version_index]
        package_multi_license_selection = package_info[self.multi_license_selection_index]

        if ' or ' in package_license.lower() or ' and ' in package_license.lower():
            # just checks that a license has been chosen
            # doesn't check that the license is actually in the multi-license (already checked when column was filled)
            if not package_multi_license_selection:
                    raise MultiLicenseCheckError(package_name, package_version, package_license)
