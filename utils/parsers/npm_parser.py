import requests
import json
import re

import js2py

from config import strings


# parser for npm versions
semver = js2py.require('semver')


class NpmPackageParser(object):

    @classmethod
    def get_package_info(cls, name, version_spec, depth, npm_sections):
        # regex to check if the package is scoped (URL is different)
        scope_regex = r"(?P<scope>@([.a-zA-Z0-9_-]|\[|\])+)/(?P<module>([.a-zA-Z0-9_-]|\[|\])+)$"
        parts = re.match(scope_regex, name)
        if parts:
            scope = parts.group('scope')
            module = parts.group('module')            
            url = f'https://registry.npmjs.org/{scope}%2F{module}/'
        else:
            url = f'https://registry.npmjs.org/{name}/'

        resp = requests.get(url)
        info = {
            name: {
                strings.REGISTRY: 'NPM',
                strings.PACKAGE: name,
            },
        }

        if resp.status_code == 200:
            package_info = json.loads(resp.content.decode())
            package_version = None
            for version in list(package_info['versions'].keys())[::-1]:
                if NpmPackageParser.satisfies(version, version_spec):
                    package_version = version
                    break
            if package_version is None:
                info[name][strings.ERROR] = 'No valid version found in NPM registry'
                return info
            info[name][strings.VERSION] = package_version
            package_info_version = package_info['versions'][package_version]

            if 'license' in package_info_version:
                if type(package_info_version['license']) is dict:
                    info[name][strings.LICENSE] = package_info_version['license']['type']
                else:
                    info[name][strings.LICENSE] = package_info_version['license']
            if 'homepage' in package_info_version:
                info[name][strings.URL] = package_info_version['homepage']
            if depth > 0:
                for section in npm_sections:
                    if section in package_info_version:
                        for dep_name in package_info_version[section].keys():
                            dep_version = package_info_version[section][dep_name]
                            dep_info = NpmPackageParser.get_package_info(
                                dep_name.lower(), dep_version, depth-1, npm_sections
                            )
                            info = {**dep_info, **info}
        else:
            info[name][strings.ERROR] = 'Package not found in NPM registry'

        return info

    @classmethod
    def satisfies(cls, version, version_spec):
        # js2py isn't perfect so we treat special cases to prevent an infinite loop...
        regex = r"(?P<maj>[0-9])\.(?P<min>[0-9])\.(?P<pat>[0-9])-?(?P<tag>[.a-z0-9]*)"
        # if only a version is given in the spec, then only this version is valid
        match = re.match(regex, version_spec)
        if match is not None and match.span() == (0, len(version_spec)):
            return version == version_spec
        if version_spec == '^' + version:
            return True
        return semver.satisfies(version, version_spec)
