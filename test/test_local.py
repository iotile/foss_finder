import os
import csv
import json
import base64
import shutil
import tempfile

import unittest2 as unittest
import pytest
from mock import patch

from foss_finder.utils.local import LocalRepository
from foss_finder.utils.tracker import FossTracker
from foss_finder.scripts import foss_finder_cli
from foss_finder.config import strings


def fake_pypi_parse_line(line, depth):
    return [{strings.REGISTRY: 'PyPi', strings.PACKAGE: line.split('=')[0], strings.LICENSE: 'MIT', strings.VERSION: '1.0'}]


def fake_npm_get_package_info(name, version, depth, npm_sections, use_semver):
    return [{strings.REGISTRY: 'NPM', strings.PACKAGE: name, strings.LICENSE: 'ISC', strings.VERSION: version}]


class LocalProjectTestCase(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.project = os.path.join(self.root, 'myproject')
        self.outdir = os.path.join(self.root, 'out')
        os.makedirs(os.path.join(self.project, 'server'))
        os.makedirs(os.path.join(self.project, 'webapp'))
        with open(os.path.join(self.project, 'requirements.txt'), 'w') as f:
            f.write('# comment\nrequests==2.0.0\n')
        with open(os.path.join(self.project, 'server', 'requirements.txt'), 'w') as f:
            f.write('flask==1.0\n')
        with open(os.path.join(self.project, 'webapp', 'package.json'), 'w') as f:
            json.dump({'dependencies': {'Left-Pad': '1.3.0'}}, f)

    def tearDown(self):
        shutil.rmtree(self.root)

    def _read_csv(self, name):
        with open(os.path.join(self.outdir, name + '.csv')) as f:
            return list(csv.reader(f))

    def _process(self, repo):
        tracker = FossTracker()
        with patch.object(foss_finder_cli.PyPiRequirementParser, 'parse_line', side_effect=fake_pypi_parse_line), \
             patch.object(foss_finder_cli.NpmPackageParser, 'get_package_info', side_effect=fake_npm_get_package_info):
            foss_finder_cli.process_project(repo, tracker, self.outdir, ['dependencies'], 0, ['/requirements.txt'])
        return tracker

    def test_repository_interface(self):
        repo = LocalRepository(self.project)
        self.assertEqual(repo.name, 'myproject')

        contents = repo.get_dir_contents('/')
        self.assertEqual([(c.name, c.type) for c in contents],
                         [('requirements.txt', 'file'), ('server', 'dir'), ('webapp', 'dir')])
        self.assertEqual([c.name for c in repo.get_dir_contents('/server')], ['requirements.txt'])

        content = repo.get_file_contents('/server/requirements.txt')
        self.assertEqual(base64.b64decode(content.content).decode('utf-8'), 'flask==1.0\n')

    def test_name_of_current_directory(self):
        cwd = os.getcwd()
        os.chdir(self.project)
        try:
            self.assertEqual(LocalRepository('.').name, 'myproject')
        finally:
            os.chdir(cwd)

    def test_not_a_directory(self):
        with self.assertRaises(ValueError):
            LocalRepository(os.path.join(self.project, 'requirements.txt'))

    def test_ignored_directories(self):
        for folder in ['.git', 'node_modules', 'venv']:
            os.makedirs(os.path.join(self.project, folder, 'sub'))
            with open(os.path.join(self.project, folder, 'sub', 'requirements.txt'), 'w') as f:
                f.write('ignored==1.0\n')
        # a virtual environment is recognized by its pyvenv.cfg file, whatever its name
        with open(os.path.join(self.project, 'venv', 'pyvenv.cfg'), 'w') as f:
            f.write('home = /usr/bin\n')

        names = [c.name for c in LocalRepository(self.project).get_dir_contents('/')]
        self.assertEqual(names, ['requirements.txt', 'server', 'webapp'])

    def test_symlinked_directories_are_not_followed(self):
        link = os.path.join(self.project, 'server', 'loop')
        try:
            os.symlink(self.project, link)
        except (OSError, NotImplementedError):
            pytest.skip('symbolic links are not supported')
        names = [c.name for c in LocalRepository(self.project).get_dir_contents('/server')]
        self.assertEqual(names, ['requirements.txt'])

    def test_process_local_project(self):
        tracker = self._process(LocalRepository(self.project))

        rows = self._read_csv('myproject')
        self.assertEqual(rows[0], ['registry', 'package', 'license', 'version', 'url', 'multi-license-selection'])
        packages = sorted(row[1] for row in rows[1:])
        self.assertEqual(packages, ['flask', 'left-pad', 'requests'])
        self.assertEqual(tracker.processed_projects['myproject'].number_of_foss, 3)

    def test_process_local_project_with_user_defined_information(self):
        with open(os.path.join(self.project, '.foss.json'), 'w') as f:
            json.dump({'add-packages': [
                {'package': 'vendored', 'version': '0.1', 'license': 'BSD', 'owner': 'John Doe'},
            ]}, f)

        self._process(LocalRepository(self.project))

        packages = sorted(row[1] for row in self._read_csv('myproject')[1:])
        self.assertEqual(packages, ['flask', 'left-pad', 'requests', 'vendored'])


class ParseArgsTestCase(unittest.TestCase):

    def test_local_does_not_need_credentials(self):
        directory = tempfile.mkdtemp()
        try:
            args = foss_finder_cli.parse_args(['--local', directory])
            self.assertEqual(args.local, directory)
            self.assertIsNone(args.token)
            self.assertIsNone(args.org)
        finally:
            shutil.rmtree(directory)

    def test_local_must_be_a_directory(self):
        with self.assertRaises(SystemExit):
            foss_finder_cli.parse_args(['--local', os.path.join(tempfile.gettempdir(), 'does-not-exist-foss-finder')])

    def test_local_excludes_github_options(self):
        directory = tempfile.mkdtemp()
        try:
            for argv in (['--local', directory, '-t', 'token'],
                         ['--local', directory, 'org'],
                         ['--local', directory, '--project', 'repo']):
                with self.assertRaises(SystemExit):
                    foss_finder_cli.parse_args(argv)
        finally:
            shutil.rmtree(directory)

    def test_github_usage_is_unchanged(self):
        args = foss_finder_cli.parse_args(['-t', 'token', 'org', '--project', 'repo'])
        self.assertEqual((args.token, args.org, args.project, args.local), ('token', 'org', 'repo', None))
        args = foss_finder_cli.parse_args(['-u', 'user', 'org'])
        self.assertEqual((args.username, args.org), ('user', 'org'))

    def test_github_usage_requires_credentials_and_org(self):
        with self.assertRaises(SystemExit):
            foss_finder_cli.parse_args(['org'])
        with self.assertRaises(SystemExit):
            foss_finder_cli.parse_args(['-t', 'token'])
