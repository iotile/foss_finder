import json
import sys

from config import config
from config.strings import *


class AdditionalInformation():
    _default_columns = config.FIELDS
    _optional_columns = ['linkage', 'justification', 'usage']
    _fields = {
        'add-packages': {
            'required': [
                PACKAGE,
                VERSION,
                LICENSE,
                OWNER,
            ],
            'optional': _default_columns,
         },
        'overwrites': {
            'required': [
                PACKAGE,
                OWNER,
                REASON,
            ],
            'optional': [VERSION] + _default_columns,
        },
        'multi-license-selection': {
            'required': [
                PACKAGE,
                OWNER,
                MULTI_LICENSE_SELECTION,
            ],
            'optional': [VERSION],
        },
        'additional-info': {
            'required': [
                PACKAGE,
                OWNER,
            ],
            'optional': [VERSION] + _optional_columns,
        },
    }

    def __init__(self, file):
        for column in (PACKAGE, VERSION, LICENSE):
            assert column in self._default_columns

        data = json.load(file)

        self._validate_data(data)
        self.add_packages = data.get('add-packages')
        self.overwrites = data.get('overwrites')
        self.multi_license_selection = data.get('multi-license-selection')
        self.additional_info = data.get('additional-info')

    def _validate_data(self, data):
        for key, packages in data.items():
            field_constraints = self._fields.get(key)
            # Check if invalid field in the config file
            if field_constraints is None:
                msg = f'Invalid field in .foss.json: {key}.'
                msg += f' Valid fields are: {", ".join(self._fields.keys)}.'
                raise ValueError(msg)
            else:
                required_fields = field_constraints['required']
                ok_fields = list(set(required_fields + field_constraints['optional']))
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

    def _find_package_info(self, package, version, data):
        # Look for an object in data matching the package and version
        # The object's 'package' field must equal package
        # The object's 'version' field must equal the version if it is specified
        query = [p for p in data if p[PACKAGE] == package and p.get(VERSION) in (None, version)]
        if not query:
            return None

        assert len(query) == 1
        package_info = query[0]
        for useless_key in (PACKAGE, VERSION, OWNER, REASON):
            package_info.pop(useless_key, None)
        return package_info

    def _process_overwrites(self, package, version, row):
        assert len(row) == len(self._default_columns)
        res = row.copy()
        
        package_info = self._find_package_info(package, version, self.overwrites)
        if package_info is None:
            return row

        for column, value in package_info.items():
            res[self._default_columns.index(column)] = value
        return res
    
    def _validate_multi_license_selection(self, selected_license, multi_license):
        raise NotImplementedError

    def _process_multi_license_selection(self, package, version, row):
        assert len(row) == len(self._default_columns) + 1
        res = row.copy()

        package_info = self._find_package_info(package, version, self.multi_license_selection)
        if package_info is None:
            return row

        selected_license = package_info[MULTI_LICENSE_SELECTION]
        self._validate_multi_license_selection(selected_license, row[self._default_columns.index(LICENSE)])
        res[-1] = selected_license
        return res

    def _process_additional_info(self, package, version, row):
        initial_row_length = len(self._default_columns) + 1
        assert len(row) == initial_row_length + len(self._optional_columns)
        res = row.copy()
        
        package_info = self._find_package_info(package, version, self.additional_info)
        if package_info is None:
            return row
        
        for column, value in package_info.items():
            res[initial_row_length + self._optional_columns.index(column)] = value
        return res

    def process_add_packages(self):
        raise NotImplementedError

    def process_package(self, package, version, row):
        if self.overwrites:
            row = self._process_overwrites(package, version, row)
        row.append('')
        if self.multi_license_selection:
            row = self._process_multi_license_selection(package, version, row)
        row.extend(len(self._optional_columns) * [''])
        if self.additional_info:
            row = self._process_additional_info(package, version, row)
        return row
