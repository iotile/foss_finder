import json
import sys

from foss_finder.config.config import DEFAULT_COLUMNS, OPTIONAL_COLUMNS
from foss_finder.config.strings import *

from .fields import AddPackages, Overwrites, MultiLicenseSelection, AdditionalInfo


class UserDefinedInformation():
    """
    Initialized from json data. It processes the data to update dependencies' information.
    - Checks if the data is correct.
    - Creates a list of rows to add to the csv file.
    - Modifies the row representing a package to add or overwrite information.
    """

    def __init__(self, data):
        for column in (PACKAGE, VERSION, LICENSE):
            assert column in DEFAULT_COLUMNS

        self._fields = {
            AddPackages.NAME: AddPackages(None),
            Overwrites.NAME: Overwrites(None),
            MultiLicenseSelection.NAME: MultiLicenseSelection(None),
            AdditionalInfo.NAME: AdditionalInfo(None),
        }
        
        self._validate_data(data)
        
        for key, field in self._fields.items():
            field.data = data.get(key)

    def _validate_data(self, data):
        for key, packages in data.items():
            field = self._fields.get(key)
            # Check if invalid field in the config file
            if field is None:
                msg = f'Invalid field in .foss.json: {key}.'
                msg += f' Valid fields are: {", ".join(self._fields.keys)}.'
                raise ValueError(msg)
            else:
                required_fields = field.required_fields
                ok_fields = list(set(required_fields + field.optional_fields))
                package_version_list = []
                # Check fields are OK for all packages
                for i, package in enumerate(packages):
                    # Check all required fields are in the config file
                    for k in required_fields:
                        if k not in package:
                            msg = f'Lacking a required field in .foss.json: {key}[{i}]["{k}"].'
                            msg += f' Required fields are: {", ".join(required_fields)}.'
                            raise ValueError(msg)
                    # Check if invalid field in the config file
                    for k in package:
                        if k not in ok_fields:
                            msg = f'Invalid field in .foss.json: {key}[{i}]["{k}"]'
                            msg += f' Valid fields are: {", ".join(ok_fields)}.'
                            raise ValueError(msg)
                    # Check there is no conflict for this package and version (only one entry)
                    package_version = (package[PACKAGE], package.get(VERSION))
                    # Version is specified: only one entry allowed for this package and version
                    if package_version[1]:
                        if package_version in package_version_list:
                            msg = f'Conflict with package {package_version[0]} version {package_version[1]}.'
                            msg += f'Only one entry allowed for this package and version.'
                            raise ValueError(msg)
                        # Check that no entry exists where no version is specified
                        elif package_version[0] in [p for p, v in package_version_list if not v]:
                            msg = f'Conflict with package {package_version[0]}.'
                            msg += f'You can only set one entry for this package if no version is given.'                            
                    # Version is not specified: only one entry allowed for this package
                    else:
                        if package_version[0] in [p for p, v in package_version_list]:
                            msg = f'Conflict with package {package_version[0]}.'
                            msg += f'You can only set one entry for this package if no version is given.'
                            raise ValueError(msg)
                    package_version_list.append(package_version)

    def added_packages(self):
        """
        Creates rows to add to the csv file (packages added by the user).
        """
        res = []
        
        if self._fields[AddPackages.NAME].data:
            initial_row = len(DEFAULT_COLUMNS) * ['']
            for pkg in self._fields[AddPackages.NAME].data:
                row = self._fields[AddPackages.NAME].process(pkg[PACKAGE], pkg[VERSION], initial_row)
                res.append(row)
        
        return res

    def process_package(self, package, version, row):
        """
        Modifies the row representing a package to add or overwrite information.
        """
        if self._fields[Overwrites.NAME].data:
            row = self._fields[Overwrites.NAME].process(package, version, row)
        
        row.append('')
        if self._fields[MultiLicenseSelection.NAME].data:
            row = self._fields[MultiLicenseSelection.NAME].process(package, version, row)
        
        row.extend(len(OPTIONAL_COLUMNS) * [''])
        if self._fields[AdditionalInfo.NAME].data:
            row = self._fields[AdditionalInfo.NAME].process(package, version, row)
        
        return row
