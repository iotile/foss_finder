import sys
import os
import json
import base64
import re
import logging
import argparse
import getpass

from github import Github, GithubException

from utils.parsers import NpmPackageParser, PyPiRequirementParser
from utils.tracker import FossTracker
from config import strings, config

logger = logging.getLogger(__name__)


def get_dir_content(repo, path, output_path, tracker):
    logger.debug(f'+++++ {path}')
    python_regex = r".*requirements.*\.txt$"
    
    try:
        files = repo.get_dir_contents(path)
    # The repository may be empty
    except GithubException:
        return None

    for file in files:
        full_path_name = os.path.join(path, file.name)
        if os.path.basename(file.name) in ['package.json', 'bower.json']:
            logger.info(f'Found {full_path_name} ({file.type})')
            file_content = repo.get_file_contents(full_path_name)
            decoded_file = base64.b64decode(file_content.content)

            obj = json.loads(decoded_file)
            for section in ['devDependencies', 'dependencies', 'engines']:
                if section in obj:
                    for name in obj[section].keys():
                        version = obj[section][name]
                        logger.debug(f'Processing module {name}: {version}')
                        info = NpmPackageParser.get_package_info(name.lower(), version)
                        logger.debug(f'Info: {info}')
                        if strings.ERROR not in info:
                            tracker.add_foss_to_project(repo.name, [info.get(f) for f in config.FIELDS])

        if re.match(python_regex, full_path_name):
            logger.info(f'Found {full_path_name} ({file.type})')
            file_content = repo.get_file_contents(full_path_name)
            decoded_file = base64.b64decode(file_content.content).decode('utf-8')
            lines = [line for line in decoded_file.split('\n') if line and line[0] != '#']

            for line in lines:
                logger.debug(f'Processing module {line}')
                info = PyPiRequirementParser.parse_line(line)
                logger.debug(f'Info: {info}')
                if strings.ERROR not in info:
                    tracker.add_foss_to_project(repo.name, [info.get(f) for f in config.FIELDS])

        if str(file.type) == 'dir':
            get_dir_content(repo, os.path.join(path, file.name), output_path, tracker)


def process_project(repo, tracker, outdir):
    output_path = os.path.join(outdir, repo.name + '.csv')
    os.makedirs(outdir, exist_ok=True)
    tracker.add_project(repo.name)
    get_dir_content(repo, '/', output_path, tracker)
    tracker.write_project_csv(repo.name, config.FIELDS, output_path)


if __name__ == '__main__':
    # Logger Format
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)-15s] %(levelname)-6s %(message)s',
        datefmt='%d/%b/%Y %H:%M:%S',
    )

    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--token', dest='token', type=str, help='Github Token')
    group.add_argument('-u', '--username', dest='username', type=str, help='Github Username')
    parser.add_argument('-o', '--outdir', dest='outdir', type=str, default='out', help='Output directory')
    parser.add_argument('--project', type=str, required=False, help='Process a specific repository')
    parser.add_argument('--debug', type=bool, default=False, help='Debug Mode')
    parser.add_argument('org', metavar='org', type=str, help='GitHub Org')

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.token:
        g = Github(args.token)
    elif args.username:
        g = Github(args.username, getpass.getpass(prompt='Github Password: '))
    else:
        logger.error('Please provide a token or a username.')

    tracker = FossTracker()

    logger.info('--------------')

    if args.project:
        repo = g.get_organization(args.org).get_repo(args.project)
        logger.info(f'Starting process for {repo.name}')
        process_project(repo, tracker, args.outdir)
        logger.info(f'End of process for {repo.name}')
        for line in tracker.report_project_summary(repo.name):
            logger.info(line)
    else:
        for index, repo in enumerate(g.get_organization(args.org).get_repos()):
            logger.info(f'Starting process for {index}: {repo.name}')
            process_project(repo, tracker, args.outdir)
            logger.info(f'End of process for {index}: {repo.name}')
        for line in tracker.report_total_summary():
            logger.info(line)
