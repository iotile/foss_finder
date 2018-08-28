from .strings import * 

# Fields of the CSV files (ordered)
FIELDS = [
    REGISTRY,
    PACKAGE,
    LICENSE,
    VERSION,
    URL,
]

# Sections of package.json/bower.json where the script looks for dependencies
NPM_SECTIONS = [
    'dependencies',
    'devDependencies',
    'peerDependencies',
    'bundledDependencies',
    'bundleDependencies',
    'optionalDependencies',
    'engines',
]
