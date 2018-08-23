import requests
import json
import re

class PyPiRequirementParser(object):

    @classmethod
    def get_package_info(cls, name, version=None):
        url = 'https://pypi.python.org/pypi/{}/'.format(name)
        if version:
            url += '{}/'.format(version)
        url += 'json'
        resp = requests.get(url)
        info = {
            'registry': 'PyPi',
            'package': name
        }
        if resp.status_code == 200:
            package_info = json.loads(resp.content.decode())
            if 'info' in package_info:
                if 'license' in package_info['info']:
                    info['license'] = package_info['info']['license']
                if 'version' in package_info['info']:
                    info['version'] = package_info['info']['version']
                if 'home_page' in package_info['info']:
                    info['url'] = package_info['info']['home_page']
                elif 'package_url' in package_info['info']:
                    info['url'] = package_info['info']['package_url']
        else:
            info['error'] = 'Package not found in PyPi'
        return info

    @classmethod
    def parse_line(cls, line):
        regex = r"(?P<name>[a-zA-Z0-9_-]+)(?P<spec>[ =<>]*)(?P<ver>[.0-9]*)"
        parts = re.match(regex, line)
        if parts:
            name = parts.group('name')
            spec = parts.group('spec').strip()
            ver = parts.group('ver')
            version = None
            if spec and ver:
                if spec in ['==', '<=']:
                    version = ver

            info = PyPiRequirementParser.get_package_info(name, version)
            return info
        return {
            'error': 'Parsing error'
        }
