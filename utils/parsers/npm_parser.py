import requests
import json
import re

from config import strings


class NpmPackageParser(object):

    @classmethod
    def get_package_info(cls, name, version=None):
        if version:
            version = NpmPackageParser.parse_version(version)

        url = 'https://registry.npmjs.org/{}/latest/'.format(name)
        #if version:
        #    url += '{}/'.format(version)

        resp = requests.get(url)
        info = {
            strings.REGISTRY: 'NPM',
            strings.PACKAGE: name,
        }
        if resp.status_code == 200:
            package_info = json.loads(resp.content.decode())
            if 'license' in package_info:
                if type(package_info['license']) is dict:
                    info[strings.LICENSE] = package_info['license']['type']
                else:
                    info[strings.LICENSE] = package_info['license']
            if 'version' in package_info:
                info[strings.VERSION] = package_info['version']
            else:
                if 'dist-tags' in package_info:
                    if 'latest' in package_info['dist-tags']:
                        info[strings.VERSION] = package_info['dist-tags']['latest']
            if 'homepage' in package_info:
                info[strings.URL] = package_info['homepage']
        else:
            info[strings.ERROR] = 'Package not found in NPM registry'
        if version:
            info[strings.VERSION] = version
        return info

    @classmethod
    def parse_version(cls, version):
        regex = r"(?P<spec>[=<>~^]*)(?P<ver>[.a-zA-Z0-9_-]*)"
        parts = re.match(regex, version)
        if parts:
            spec = parts.group('spec').strip()
            ver = parts.group('ver')
            version = ver
            if spec and ver:
                if spec in ['>=', '>']:
                    version = None

            return version
        raise ValueError
