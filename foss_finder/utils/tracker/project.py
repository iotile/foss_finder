from foss_finder.config.config import DEFAULT_COLUMNS, OPTIONAL_COLUMNS
from foss_finder.config.strings import PACKAGE, VERSION, MULTI_LICENSE_SELECTION

from ..user_defined_info import UserDefinedInformation


class Project():
    """
    Represents a project. Stores the list of its dependencies.
    """

    def __init__(self, name, global_user_defined_information):
        self.name = name
        self.global_user_defined_information = global_user_defined_information
        self.user_defined_information = None
        self.list_of_foss = []

    @property
    def number_of_foss(self):
        return len(self.list_of_foss)

    @property
    def columns(self):
        if self.user_defined_information:
            return DEFAULT_COLUMNS + [MULTI_LICENSE_SELECTION] + OPTIONAL_COLUMNS
        else:
            return DEFAULT_COLUMNS

    @property
    def summary(self):
        return [
            '--------------',
            f'Project {self.name}:',
            f'Number of open source projects found: {self.number_of_foss}',
        ]

    def set_user_defined_information(self, local_data):
        self.user_defined_information = UserDefinedInformation(local_data, self.global_user_defined_information)
        for foss in self.user_defined_information.added_packages():
            self.add_foss(foss)

    def add_foss(self, foss):
        if self.user_defined_information:
            package = foss[DEFAULT_COLUMNS.index(PACKAGE)]
            version = foss[DEFAULT_COLUMNS.index(VERSION)]
            processed_foss = self.user_defined_information.process_package(package, version, foss)
            if processed_foss not in self.list_of_foss:
                self.list_of_foss.append(processed_foss)
        else:
            if foss not in self.list_of_foss:
                self.list_of_foss.append(foss)
