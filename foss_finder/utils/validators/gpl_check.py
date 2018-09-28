import foss_finder.config.config
from foss_finder.config.strings import LICENSE, PACKAGE, VERSION

from .base import Check, CheckError


class GPLCheckError(CheckError):
    """
    Raised when the GPL check doesn't pass. (The package is licensed under a GPL-like license.)
    """

    def __init__(self, package_name, package_version, package_license):
        self.package_name = package_name
        self.package_version = package_version
        self.package_license = package_license
        self.message = f'Package {package_name} version {package_version} is licensed under {package_license}.'


class GPLCheck(Check):
    """
    Checks that the license is not a GPL license. (Or AGPL, LGPL, etc.)
    """
    NAME = 'GPL Check'
    DESCRIPTION = 'Checks that the license is not a GPL-like license'

    def __init__(self, *args, **kwargs):
        default_colummns = foss_finder.config.config.DEFAULT_COLUMNS
        if LICENSE in default_colummns and PACKAGE in default_colummns and VERSION in default_colummns:
            self.license_index = default_colummns.index(LICENSE)
            self.name_index = default_colummns.index(PACKAGE)
            self.version_index = default_colummns.index(VERSION)
        else:
            raise ValueError('Package, version, and license must be in the default columns.')

    def check(self, package_info):
        package_license = package_info[self.license_index]
        package_name = package_info[self.name_index]
        package_version = package_info[self.version_index]

        if 'gpl' in package_license.lower():
            raise GPLCheckError(package_name, package_version, package_license)
