from foss_finder.config.config import USER_DEFINED_INFORMATION_FIELDS
from foss_finder.config.strings import *


class UserDefinedInformationField():
    """
    Abstract class to implement the fields of the user-defined information file.
    A field of the user-defined information file is meant to contain an array of
    packages whose information must be added, completed, or modified.
    """
    # must be defined by the derived class
    NAME = None

    def __init__(self, data):
        self.data = data
        self.required_fields, self.optional_fields = USER_DEFINED_INFORMATION_FIELDS[self.NAME]
        self._package_info_useless_keys = (PACKAGE, VERSION, OWNER, REASON)

    def _find_package_info(self, package, version):
        # Look for an object in data matching the package and version
        # The object's 'package' field must equal package
        # The object's 'version' field must equal the version if it is specified
        query = [p for p in self.data if p[PACKAGE] == package and p.get(VERSION) in (None, version)]
        if not query:
            return None

        assert len(query) == 1
        package_info = query[0].copy()
        for useless_key in self._package_info_useless_keys:
            package_info.pop(useless_key, None)
        return package_info
    
    def _transform_row(self, row, package_info):
        """
        Abstract method: must be implemented by the derived class
        Return the updated row by using the package info
        """
        raise NotImplementedError

    def process(self, package, version, row):
        package_info = self._find_package_info(package, version)
        if package_info is None:
            return row
        return self._transform_row(row, package_info)
