from setuptools import setup, find_packages
from version import version

setup(
    name="foss_finder",
    packages=find_packages(exclude=("test",)),
    version=version,
    install_requires=[
        "requirements-parser == 0.1.0",
        "PyGithub"
    ],
    entry_points={
        'console_scripts': [
            'foss-finder-cli = foss_finder.scripts.foss_finder_cli:main'
        ]
    },
    include_package_data=True,
    description="Finds Open Source dependencies for a GitHub Organization and/or Project",
    license='MIT',
    author="Arch Systems Inc",
    author_email="info@archsys.io",
    url="https://github.com/iotile/foss_finder",
    keywords=["FOSS", "Open Source", "Licenses"],
    classifiers=[
        "Programming Language :: Python",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
    long_description="""\
FOSS_FINDER
-----------

The script is fairly easy to use but if you need any help, you can run:

```
python foss_finder_cli.py -h
```

The standard way to run the script is to get an access token for your GitHub organization, then run:

```
python foss_finder_cli.py -t <your_access_token> <name_of_your_organization>
```

Alternatively, you can directly use your GitHub username to login:

```
python foss_finder_cli.py -u <your_username> <name_of_your_organization>
```
"""
)
