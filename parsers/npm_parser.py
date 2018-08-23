import requests
import json

class NpmPackageParser(object):

    @classmethod
    def get_package_info(cls, name, version=None):
        if version:
            for char_to_remove in '~^=<>':
                version = version.replace(char_to_remove, '')

        url = 'https://registry.npmjs.org/{}/latest/'.format(name)
        #if version:
        #    url += '{}/'.format(version)
        print(url)
        resp = requests.get(url)
        info = {
            'registry': 'NPM',
            'package': name
        }
        if resp.status_code == 200:
            package_info = json.loads(resp.content.decode())
            if 'license' in package_info:
                info['license'] = package_info['license']
            if 'version' in package_info:
                info['version'] = package_info['version']
            else:
                if 'dist-tags' in package_info:
                    if 'latest' in package_info['dist-tags']:
                        info['version'] = package_info['dist-tags']['latest']
            if 'homepage' in package_info:
                info['url'] = package_info['homepage']
        else:
            info['error'] = 'Package not found in NPM registry'
        return info
