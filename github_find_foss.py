import sys
import os
import json
import base64
import logging
import argparse

from github import Github

from utils.parsers import NpmPackageParser, PyPiRequirementParser
from utils.csv import write_new_row
from config import strings, config

logger = logging.getLogger(__name__)


def get_dir_content(repo, path):
    logger.debug(f'+++++ {path}')
    files = repo.get_dir_contents(path)
    for file in files:
        if os.path.basename(file.name) in ['package.json', 'bower.json']:
            full_path_name = os.path.join(path, file.name)
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
                            write_new_row(output_path, [info.get(f) for f in config.FIELDS])


        if os.path.basename(file.name) in ['requirements.txt', 'base.txt', 'development.txt', 'docker.txt', 'production.txt']:
            full_path_name = os.path.join(path, file.name)
            logger.info(f'Found {full_path_name} ({file.type})')
            file_content = repo.get_file_contents(full_path_name)
            decoded_file = base64.b64decode(file_content.content).decode('utf-8')
            lines = [line for line in decoded_file.split('\n') if line and line[0] != '#']

            for line in lines:
                logger.debug(f'Processing module {line}')
                info = PyPiRequirementParser.parse_line(line)
                logger.debug(f'Info: {info}')
                if strings.ERROR not in info:
                    write_new_row(output_path, [info.get(f) for f in config.FIELDS])

        if str(file.type) == 'dir':
            get_dir_content(repo, os.path.join(path, file.name), output_path)


if __name__ == '__main__':
    # Logger Format
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)-15s] %(levelname)-6s %(message)s',
        datefmt='%d/%b/%Y %H:%M:%S',
    )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--token', dest='token', type=str, required=False, help='Github Token')
    parser.add_argument('-o', '--outdir', dest='outdir', type=str, default='out', help='Output directory')
    parser.add_argument('--debug', type=bool, default=False, help='Debug Mode')
    parser.add_argument('org', metavar='org', type=str, help='GitHub Org')

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.info('--------------')

    # Uses an access token
    if args.token:
        access_token = args.token
    else:
        access_token = input('GitHub Access Token? ')

    g = Github(access_token)

    for index, repo in enumerate(g.get_organization(args.org).get_repos()):
        logger.info(f'Starting process for {index}: {repo.name}')
        output_path = os.path.join(args.outdir, repo.name + '.csv')
        os.makedirs(args.outdir, exist_ok=True)
        write_new_row(output_path, config.FIELDS)
        get_dir_content(repo, '/', output_path)
        logger.info(f'End of process for {index}: {repo.name}')
