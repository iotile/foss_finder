import sys
import os
import json
import base64
import logging
import argparse

from github import Github

from parsers.npm_parser import NpmPackageParser

logger = logging.getLogger(__name__)


def get_dir_content(repo, path):
    print('+++++ {}'.format(path))
    files = repo.get_dir_contents(path)
    for file in files:
        if os.path.basename(file.name) in ['package.json']:
            full_path_name = os.path.join(path, file.name)
            print('--> {} ({})'.format(full_path_name, file.type))
            file_content = repo.get_file_contents(full_path_name)
            decoded_file = base64.b64decode(file_content.content)
            # print(decoded_file)

            obj = json.loads(decoded_file)
            for section in ['devDependencies', 'dependencies', 'engines']:
                if section in obj:
                    for name in obj[section].keys():
                        version = obj[section][name]
                        print('----> {}: {}'.format(name, version))
                        info = NpmPackageParser.get_package_info(name, version)
                        print('----> {}'.format(info))

        if str(file.type) == 'dir':
            get_dir_content(repo, os.path.join(path, file.name))


# Then play with your Github objects:

if __name__ == '__main__':

    # First create a Github instance:

    # Test
    # Logger Format
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)-15s] %(levelname)-6s %(message)s',
                        datefmt='%d/%b/%Y %H:%M:%S')

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--token', dest='token', type=str, required=False, help='Github Token')
    parser.add_argument('org', metavar='org', type=str, help='GitHub Org')

    args = parser.parse_args()
    logger.info('--------------')

    # or using an access token
    if args.token:
        access_token = args.token
    else:
        access_token = input('GitHub Access Token? ')

    g = Github(access_token)

    index = 0
    for repo in g.get_organization(args.org).get_repos():
        print('{}: {}'.format(index, repo.name))

        get_dir_content(repo, '/')

        index += 1
        sys.exit()



