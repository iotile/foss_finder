from ..user_defined_info import UserDefinedInformation


class Project():

    def __init__(self, name):
        self.name = name
        self.list_of_foss = []
        self.user_defined_information = None

    @property
    def number_of_foss(self):
        return len(self.list_of_foss)

    @property
    def summary(self):
        return [
            '--------------',
            f'Project {self.name}:',
            f'Number of open source projects found: {self.number_of_foss}',
        ]

    def add_user_defined_information(self, filename):
        self.user_defined_information = UserDefinedInformation(filename)

    def add_foss(self, foss):
        if foss not in self.list_of_foss:
            self.list_of_foss.append(foss)
