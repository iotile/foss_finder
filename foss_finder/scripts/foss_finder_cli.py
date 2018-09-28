import sys
import os
import json
import base64
import re
import logging
import argparse
import getpass

from github import Github, GithubException

from ..utils.parsers import NpmPackageParser, PyPiRequirementParser
from ..utils.tracker import FossTracker
from ..config import strings, config

logger = logging.getLogger(__name__)


def get_dir_content(repo, path, output_path, tracker, npm_sections, depth, python_files):
    logger.debug(f'+++++ {path}')
    python_regex = r".*requirements.*\.txt$"
    
    try:
        files = repo.get_dir_contents(path)
    # The repository may be empty
    except GithubException:
        return None

    if path == '/':
        if config.USER_DEFINED_INFORMATION_NAME in [file.name for file in files]:
            full_path_name = os.path.join(path, config.USER_DEFINED_INFORMATION_NAME)
            logger.info(f'Found {full_path_name} (user-defined information file)')
            file_content = repo.get_file_contents(full_path_name)
            decoded_file = base64.b64decode(file_content.content)
            data = json.loads(decoded_file)
            logger.debug(f'Found the following data: {data}')
            tracker.add_user_defined_information_to_project(repo.name, data)
        # If no user-defined information file is found, we still want to process packages to add empty columns
        else:
            logger.debug(f'No user-defined information file was found')
            data = {}
            tracker.add_user_defined_information_to_project(repo.name, data)

    for file in files:
        full_path_name = os.path.join(path, file.name)
        if os.path.basename(file.name) in ['package.json', 'bower.json']:
            logger.info(f'Found {full_path_name} ({file.type})')
            file_content = repo.get_file_contents(full_path_name)
            decoded_file = base64.b64decode(file_content.content)

            obj = json.loads(decoded_file)
            for section in npm_sections:
                if section in obj:
                    for name in obj[section].keys():
                        version = obj[section][name]
                        logger.debug(f'Processing module {name}: {version}')
                        info = NpmPackageParser.get_package_info(name.lower(), version, depth, npm_sections, config.USE_SEMVER)
                        logger.debug(f'Info: {info[0]}')
                        for pkg_info in info:
                            if strings.ERROR not in pkg_info:
                                tracker.add_foss_to_project(repo.name, [pkg_info.get(f) for f in config.DEFAULT_COLUMNS])

        if any([name in full_path_name for name in python_files]):
            logger.info(f'Found {full_path_name} ({file.type})')
            file_content = repo.get_file_contents(full_path_name)
            decoded_file = base64.b64decode(file_content.content).decode('utf-8')
            lines = [line for line in decoded_file.split('\n') if line and line[0] != '#']

            for line in lines:
                logger.debug(f'Processing module {line}')
                info = PyPiRequirementParser.parse_line(line, depth)
                logger.debug(f'Info: {info[0]}')
                for pkg_info in info:
                    if strings.ERROR not in pkg_info:
                        tracker.add_foss_to_project(repo.name, [pkg_info.get(f) for f in config.DEFAULT_COLUMNS])

        if str(file.type) == 'dir':
            get_dir_content(repo, os.path.join(path, file.name), output_path, tracker, npm_sections, depth, python_files)


def process_project(repo, tracker, outdir, npm_sections, depth, python_files):
    output_path = os.path.join(outdir, repo.name + '.csv')
    os.makedirs(outdir, exist_ok=True)
    tracker.add_project(repo.name)
    get_dir_content(repo, '/', output_path, tracker, npm_sections, depth, python_files)
    tracker.write_project_csv(repo.name, output_path)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--token', dest='token', type=str, help='GitHub token')
    group.add_argument('-u', '--username', dest='username', type=str, help='GitHub username')
    parser.add_argument('-o', '--outdir', dest='outdir', type=str, default='out', help='output directory')
    parser.add_argument('--depth', dest='depth', type=int, default=0, help='depth for NPM and Python dependencies')
    parser.add_argument('--project', type=str, required=False, help='process a specific repository')
    parser.add_argument('--dev', action='store_true', help='activate lookup for dev dependencies')
    parser.add_argument('--debug', action='store_true', help='debug mode')
    parser.add_argument('org', metavar='org', type=str, help='GitHub organization')

    return parser


def main():
    # Logger Format
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)-15s] %(levelname)-6s %(message)s',
        datefmt='%d/%b/%Y %H:%M:%S',
    )
    parser = build_parser()
    args = parser.parse_args()

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.debug(f'Config: use semver? {config.USE_SEMVER}')
    logger.debug(f'Config: NPM sections: {config.NPM_SECTIONS}')
    logger.debug(f'Config: Python files: {config.PYTHON_FILES}')
    logger.debug(f'Config: ignored repositories: {config.IGNORED_REPOS}')

    # NPM sections and Python files
    npm_sections = config.NPM_SECTIONS[strings.PRODUCTION]
    python_files = config.PYTHON_FILES[strings.PRODUCTION]
    if args.dev:
        npm_sections.extend(config.NPM_SECTIONS[strings.DEVELOPMENT])
        npm_sections = list(set(npm_sections))
        python_files.extend(config.PYTHON_FILES[strings.DEVELOPMENT])
        python_files = list(set(python_files))

    try:
        if args.token:
            g = Github(args.token)
            organization = g.get_organization(args.org)
        elif args.username:
            g = Github(args.username, getpass.getpass(prompt='Github Password: '))
            organization = g.get_organization(args.org)
        else:
            logger.critical('Please provide a token or a username')
            sys.exit()
    except GithubException:
        logger.critical('Bad credentials')
        sys.exit()

    logger.info('--------------')

    try:
        with open(config.GLOBAL_USER_DEFINED_INFORMATION_NAME) as f:
            global_user_defined_information = json.load(f)
        logger.info(f'Found {config.GLOBAL_USER_DEFINED_INFORMATION_NAME} (global user-defined information file)')
        logger.debug(f'Found the following data: {global_user_defined_information}')
    except FileNotFoundError:
        global_user_defined_information = {}
        logger.debug(f'No global user-defined information file was found')

    tracker = FossTracker(global_user_defined_information=global_user_defined_information)

    if args.project:
        repo = organization.get_repo(args.project)
        logger.info(f'Starting process for {repo.name}')
        process_project(repo, tracker, args.outdir, npm_sections, args.depth, python_files)
        logger.info(f'End of process for {repo.name}')
        for line in tracker.report_project_summary(repo.name):
            logger.info(line)
    else:
        for index, repo in enumerate(organization.get_repos()):
            logger.info(f'Starting process for {index}: {repo.name}')
            if repo.name not in config.IGNORED_REPOS:
                process_project(repo, tracker, args.outdir, npm_sections, args.depth, python_files)
            else:
                logger.info('Ignored')
            logger.info(f'End of process for {index}: {repo.name}')
        for line in tracker.report_total_summary():
            logger.info(line)

    return 0

