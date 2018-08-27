from ..csv import write_new_row


class FossTracker():
    def __init__(self):
        # Maps the name of a project to the list of infos of found foss
        self.processed_projects = {}
    
    @property
    def number_of_projects_processed(self):
        return len(self.processed_projects)
    
    @property
    def number_of_foss_found(self):
        total_list_of_foss = []
        for list_of_foss in self.processed_projects.values():
            list_of_foss_strings = [','.join([i if i else '' for i in foss_info]) for foss_info in list_of_foss]
            total_list_of_foss.extend(list_of_foss_strings)
        no_duplicate_list_of_foss = list(set(total_list_of_foss))
        return len(no_duplicate_list_of_foss)

    def add_project(self, project):
        if project not in self.processed_projects:
            self.processed_projects[project] = []
    
    def add_foss_to_project(self, project, foss):
        list_of_foss = self.processed_projects[project]
        if foss not in list_of_foss:
            list_of_foss.append(foss)

    def write_project_csv(self, project, fields, filename):
        write_new_row(filename, fields)
        list_of_foss = self.processed_projects[project]
        for foss in list_of_foss:
            write_new_row(filename, foss)

    def report_project_summary(self, project):
        number_of_foss = len(self.processed_projects[project])
        return [
            '--------------',
            f'Project {project}:',
            f'Number of open source projects found: {number_of_foss}',
        ]
    
    def report_total_summary(self):
        return [
            '--------------',
            f'Total number of GitHub projects processed: {self.number_of_projects_processed}',
            f'Total number of open source projects found: {self.number_of_foss_found}',
        ]
