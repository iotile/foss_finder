import requests
import json
import re

from foss_finder.config import strings, config


semver = None
if config.USE_SEMVER:
    try:
        import js2py

        # parser for npm versions
        semver = js2py.require('semver')
    except Exception as e:
        print(e)


class NpmPackageParser(object):

    @classmethod
    def get_package_info(cls, name, version_spec, depth, npm_sections, use_semver=False):
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
        info = [
            {
                strings.REGISTRY: 'NPM',
                strings.PACKAGE: name,
            }
        ]

        if resp.status_code == 200:
            package_info = json.loads(resp.content.decode())
            package_version = None
            for version in list(package_info['versions'].keys())[::-1]:
                if cls.satisfies(version, version_spec, use_semver=use_semver):
                    package_version = version
                    break
            if package_version is None:
                info[0][strings.ERROR] = 'No valid version found in NPM registry'
                return info
            info[0][strings.VERSION] = package_version
            package_info_version = package_info['versions'][package_version]

            if 'license' in package_info_version:
                if type(package_info_version['license']) is dict:
                    info[0][strings.LICENSE] = package_info_version['license']['type']
                else:
                    info[0][strings.LICENSE] = package_info_version['license']
            elif 'licenses' in package_info_version:
                if len(package_info_version['licenses']) == 1:
                    info[0][strings.LICENSE] = package_info_version['licenses'][0]['type']
                else:
                    info[0][strings.LICENSE] = '(' + ' OR '.join([lic['type'] for lic in package_info_version['licenses']]) + ')'
            if 'homepage' in package_info_version:
                info[0][strings.URL] = package_info_version['homepage']
            if depth > 0:
                for section in npm_sections:
                    if section in package_info_version:
                        for dep_name in package_info_version[section].keys():
                            dep_version = package_info_version[section][dep_name]
                            dep_info = cls.get_package_info(
                                dep_name.lower(), dep_version, depth-1, npm_sections, use_semver=use_semver
                            )
                            # update info with no duplicate
                            for pkg_info in dep_info:
                                if pkg_info not in info:
                                    info.append(pkg_info)
        else:
            info[0][strings.ERROR] = 'Package not found in NPM registry'

        return info

    @classmethod
    def satisfies(cls, version, version_spec, use_semver=False):
        if use_semver and semver:
            # js2py isn't perfect so we treat special cases to prevent an infinite loop...
            if version_spec == '^' + version:
                return True
            if version_spec == "*":
                return True
            regex = r"(?P<maj>[0-9]+)\.(?P<min>[0-9]+)\.(?P<pat>[0-9]+)-?(?P<tag>[.a-z0-9]*)"
            # if only a version is given in the spec, then only this version is valid
            match = re.match(regex, version_spec)
            if match is not None and match.span() == (0, len(version_spec)):
                return version == version_spec
            return semver.satisfies(version, version_spec)
        else:
            version_regex = r"(?P<maj>[0-9]+)(\.(?P<min>[0-9]+))?(\.(?P<pat>[0-9]+))?-?(?P<tag>[.a-z0-9]*)"
            spec_regex = r"(?P<spec>[ ~^><=*]*)(?P<maj>[0-9]+)?(\.(?P<min>[0-9]+))?(\.(?P<pat>[0-9]+))?-?(?P<tag>[.a-z0-9]*)"
            ac_parts = re.match(version_regex, version)
            parts= re.match(spec_regex, version_spec)
            if ac_parts:
                ac_v_elts = [
                    ac_parts.group('maj'),
                    ac_parts.group('min') or '0',
                    ac_parts.group('pat') or '0',
                ]
            else:
                raise ValueError(version)
            if parts:
                spec = parts.group('spec').replace(' ', '')
                v_elts = [
                    parts.group('maj'),
                    parts.group('min') or '0',
                    parts.group('pat') or '0',
                ]
            else:
                raise ValueError(version_spec)
            if spec == "*":
                return True
            elif spec == '<':
                for i in range(3):
                    if ac_v_elts[i] != v_elts[i]:
                        return ac_v_elts[i] < v_elts[i]
                return False
            elif spec == '<=':
                for i in range(3):
                    if ac_v_elts[i] != v_elts[i]:
                        return ac_v_elts[i] < v_elts[i]
                return True
            elif spec == '>':
                for i in range(3):
                    if ac_v_elts[i] != v_elts[i]:
                        return ac_v_elts[i] > v_elts[i]
                return False
            elif spec == '>=':
                for i in range(3):
                    if ac_v_elts[i] != v_elts[i]:
                        return ac_v_elts[i] > v_elts[i]
                return True
            elif spec == '=' or spec == '':
                return ac_v_elts == v_elts
            elif spec == '~':
                return cls.satisfies(version, f'>={v_elts[0]}.{v_elts[1]}.{v_elts[2]}') \
                    and cls.satisfies(version, f'<{v_elts[0]}.{int(v_elts[1]) + 1}.0')
            elif spec == '^':
                if v_elts[0]:
                    new_version_spec = f'<{int(v_elts[0]) + 1}.0.0'
                elif v_elts[1]:
                    new_version_spec = f'<0.{int(v_elts[1]) + 1}.0'
                else:
                    new_version_spec = f'<0.0.{int(v_elts[2]) + 1}'
                return cls.satisfies(version, f'>={v_elts[0]}.{v_elts[1]}.{v_elts[2]}') \
                    and cls.satisfies(version, new_version_spec)
            else:
                raise ValueError('error')
