import os
import base64


class LocalContent():
    """
    Represents a file or a directory of a local project.
    Mimics the attributes of the GitHub content objects that the scanner uses.
    """

    def __init__(self, name, type, content=None):
        self.name = name
        self.type = type
        self.content = content


class LocalRepository():
    """
    Represents a project stored on the local file system.
    Exposes the same interface as the GitHub repository objects that the scanner uses
    so that a local project can be processed exactly like a GitHub repository.
    """

    # Directories that never contain the project's own dependency files
    IGNORED_DIRECTORIES = ['.git', '.hg', '.svn', 'node_modules']

    def __init__(self, root, name=None):
        self.root = os.path.abspath(root)
        if not os.path.isdir(self.root):
            raise ValueError(f'{root} is not a directory')
        self.name = name if name else (os.path.basename(self.root) or self.root)

    def _local_path(self, path):
        # Paths are given relatively to the root of the project, e.g. '/' or '/folder/package.json'
        return os.path.join(self.root, *[part for part in path.split('/') if part])

    def _is_ignored(self, local_path):
        if os.path.basename(local_path) in self.IGNORED_DIRECTORIES:
            return True
        # Virtual environments contain the files of installed packages, not the project's dependency files
        return os.path.isfile(os.path.join(local_path, 'pyvenv.cfg'))

    def get_dir_contents(self, path):
        local_dir = self._local_path(path)
        contents = []
        for name in sorted(os.listdir(local_dir)):
            local_path = os.path.join(local_dir, name)
            if os.path.isdir(local_path):
                # Symbolic links to directories are not followed (they could create cycles)
                if not os.path.islink(local_path) and not self._is_ignored(local_path):
                    contents.append(LocalContent(name, 'dir'))
            elif os.path.isfile(local_path):
                contents.append(LocalContent(name, 'file'))
        return contents

    def get_file_contents(self, path):
        with open(self._local_path(path), 'rb') as f:
            content = base64.b64encode(f.read())
        return LocalContent(os.path.basename(path), 'file', content)
