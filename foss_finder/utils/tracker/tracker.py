from foss_finder.utils.csv import write_new_row
from foss_finder.utils.user_defined_info import UserDefinedInformation

from .project import Project


class FossTracker():
    """
    Tracks a set of projects along with their dependencies.
    """

    def __init__(self, global_user_defined_information={}):
        # validate global data only one time
        UserDefinedInformation.validate_data(global_user_defined_information)
        self.global_user_defined_information = global_user_defined_information
        # Maps the name of a project to a Project object
        self.processed_projects = {}
    
    @property
    def number_of_projects_processed(self):
        return len(self.processed_projects)
    
    @property
    def number_of_foss_found(self):
        total_list_of_foss = []
        for list_of_foss in [project.list_of_foss for project in self.processed_projects.values()]:
            list_of_foss_strings = [','.join([i if i else '' for i in foss_info]) for foss_info in list_of_foss]
            total_list_of_foss.extend(list_of_foss_strings)
        no_duplicate_list_of_foss = list(set(total_list_of_foss))
        return len(no_duplicate_list_of_foss)

    def add_project(self, project_name):
        if project_name not in self.processed_projects:
            self.processed_projects[project_name] = Project(project_name, self.global_user_defined_information)
    
    def add_user_defined_information_to_project(self, project_name, data):
        self.processed_projects[project_name].set_user_defined_information(data)

    def add_foss_to_project(self, project_name, foss):
        self.processed_projects[project_name].add_foss(foss)

    def write_project_csv(self, project_name, filename):
        project = self.processed_projects[project_name]
        write_new_row(filename, project.columns)
        for foss in project.list_of_foss:
            write_new_row(filename, foss)

    def report_project_summary(self, project_name):
        return self.processed_projects[project_name].summary
    
    def report_total_summary(self):
        return [
            '--------------',
            f'Total number of GitHub projects processed: {self.number_of_projects_processed}',
            f'Total number of open source projects found: {self.number_of_foss_found}',
        ]
