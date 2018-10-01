# FOSS Finder

A Python script to look for the dependencies used in the repositories of a GitHub organization.

## Installation

When it comes to using Python packages, it is always recommended you use a Python Virtual Env. Using Python 3, you can simply do:

```shell
python3 -m venv  ~/.virtualenv/foss_finder
source ~/.virtualenv/foss_finder/bin/activate
```

Once the virtual environment is set up, simply install the dependencies with:

```shell
pip install -U pip
pip install -U foss_finder
```

## How to use the script

### Basic usage

The script is fairly easy to use but if you need any help, you can run:

```shell
foss-finder-cli -h
```

The standard way to run the script is to get an access token for your GitHub organization, then run:

```shell
foss-finder-cli -t <your_access_token> <name_of_your_organization>
```

Alternatively, you can directly use your GitHub username to login:

```shell
foss-finder-cli -u <your_username> <name_of_your_organization>
```

**_NB:_** Don't forget to have the INI configuration file in the same directory as the one where you run the command! (See below: _Configuration_.)

### Other options

The above commands run the script on all the repositories of the organization. If you want to process a single repository, you can do so by adding `--project <name_of_your_repository>`.

By default, the reports are stored in csv format in a directory named _out_. The names of the reports are _<name_of_your_repository>.csv_. You can change the directory where these csv files are saved by adding `-o <relative_path_of_directory>`.

By default, for a given project, the script only looks for the direct dependencies of the project (not the dependencies of the dependencies of the project for example). However, it is possible to look for deep dependencies by adding `--depth <int:depth>`.

By default, the script only looks for production dependencies. If you wish to look for development and build dependencies too, then you can add `--dev`. Production vs development dependencies are defined by the INI configuration file. (See below: _Configuration_.)

Finally, you can add `--debug` to enable debug mode.

### Configuration

The main config file for the script is `/config/config.py` but you shouldn't have to modify it as a user.

The `INI_PATH` value defines the path of the INI configuration file, which is the file you want to change to get the script doing what you want.

By default, this INI configuration file is named *.foss_finder*. It contains six different sections and several keys. If a key is meant to be a list and you want the list to be empty, you can use the following syntax:

```ini
[Section]
key=
```

You can remove sections, but don't remove required keys from sections.

When using the CLI, make sure you have the INI configuration file in the same directory as the one where you run the commands. The next paragraphs will explain what are the sections of the INI configurastion file.

**_NB:_** `/config/config.py` also defines other values that you can't change in the INI configuration file, such as `DEFAULT_COLUMNS`, `USER_DEFINED_INFORMATION_NAME`, `GLOBAL_USER_DEFINED_INFORMATION_NAME`, and `USER_DEFINED_INFORMATION_FIELDS`. There is no reason for a user to change these values.

#### User defined information

As a user, you can add information to the csv files that are generated by the script. This process will be explained below (see: _User defined information (modify the csv files)_) but one of the things you can do is to add extra columns to the csv files. For instance, let's say you want to add a column named 'justification' to explain why your closed-source software is using a dependency whose license is GPL. Then, you can add _justification_ to the `optional_columns` key and this column will be created. (To see how to fill it, see: _User defined information (modify the csv files)_).

#### NPM parser

`use_semver` is a boolean. _semver_ is a NPM package (https://github.com/npm/node-semver) that is used by NPM to parse the version contraints in _package.json_.  
By default, the script doesn't use _semver_ because it introduces a dependency to NPM (and NodeJS). Instead, it uses a simple parser made in Python. You can still set `use_semver` to `true` to try to use _semver_ and get better results. In this case, don't forget to install NodeJS and NPM. However, there is no need to install _semver_ as _js2py_ will do it automatically.

#### NPM sections

The keys define the sections that are looked for inside _package.json_ and _bower.json_ (NPM dependencies). `npm_prod` defines the sections which correspond to production and `npm_dev` defines the sections which correspond to development (they are looked for when you use the `--dev` argument).

#### Python files

The keys define the files that are looked for (Python dependencies). `py_prod` corresponds to the production files and `py_dev` corresponds to the development files.  
The files that are looked for are those whose name contains the name of one of the files defined here. For instance, if `py_prod` contains _/requirements.txt_, then the following files will match: _/requirements.txt_, _/somefolder/requirements.txt_. So, be careful to include the '/' because if it contained _requirements.txt_, then _dev_requirements.txt_ would match!

#### Checks

You may want to validate the information of your dependencies and exit the script with an error if the information is not valid (for example if you want to use foss_finder as a tool for Continuous Integration).  
`validators` is the list of validators that are used to check the information of your dependencies. They raise an error when a package doesn't pass the check.

There are currently two validators you can use:
- **gpl_forbidden**: checks that your dependencies are not licensed under a GPL-like license.
- **multi_license_selection**: checks that you chose a license for your multi-licensed dependencies.

#### Ignored repositories

`ignored_repos` is simply the list of the repositories which should be ignored. If a repo contains no dependency but does have multiple different folders, you want to include it here so that the script doesn't waste a lot of time trying to find dependencies in all these folders.

## User defined information (modify the csv files)

### Context

When tracking FOSS, it can be convenient to modify the output for several purposes. For instance:
1) Indicate which license we are using when the project is multi-license.
2) Be able to explain exceptions.
3) Be able to indicate that a given project is only used internally.

That's why foss_finder gives the possibility to modify the csv files that are generated by the script in several ways. There are currently four ways to modify the files:
1) **Add dependencies**: manually add information about packages that couldn't be found by foss_finder.
2) **Overwrite a dependency information**: manually modify incorrect information about a dependency (for instance: the license is not MIT but BSD).
3) **Select a license from a multi-license**: some packages are multi-licensed. You can manually choose which license you are using.
4) **Add information about a dependency**: manually add information about a package in an optional column (for instance: provide a justification for using a package whose license is a GPL).

### How to add user defined information

You can modify the csv file of a repository by adding a configuration file at the root of the repository. By default, this file should be named _.foss.json_. If this file is found, the foss_finder script parses it and uses the information to modify the output csv file of the repository.

Here is an example of what you can put in this file:

```json
{
  "overwrites": [
    {
      "package": "Foo",
      "version": "1.2.3",
      "license": "MIT",
      "reason": "License was not found but this is actually MIT.",
      "owner": "John Doe"
    }
  ],
  "additional-info": [
    {
      "package": "Bar",
      "justification": "We don't distribute this software.",
      "owner": "John Doe"
    }
  ],
  "add-packages": [
    {
      "package": "Foo2",
      "version": "3.2.1",
      "license": "(MIT OR Apache License 2.0)",
      "registry": "NPM",
      "owner": "Jane Doe"
    },
    {
      "package": "Bar2",
      "version": "4.2",
      "license": "BSD-3",
      "owner": "John Doe"
    }
  ],
  "multi-license-selection": [
    {
      "package": "Foo2",
      "version": "3.2.1",
      "multi-license-selection": "Apache License 2.0",
      "owner": "Jane Doe"
    }
  ]
}
```

Let's explain what happens field by field:
1) `"overwrites"`: overwrite package _Foo_ version _1.2.3_ by changing the value of the _license_ column to _MIT_. A reason must be provided in the `"reason"` field to justify this change.
2) `"additional-info"`: add a value to the optional column _justification_ for package _Bar_. _justification_ must be provided in the `optional_columns` key of the INI configuration file. (See above: _Configuration_.)
3) `"add-packages"`: add packages to the output csv file (basically add rows). Basic information must be provided for these packages: fields `"package"`, `"version"`, and `"license"` are required. Only the default columns can be provided here. If you want to add optional columns or choose a license, you must do this in the corresponding field.
4) `"multi-license-selection"`: for package _Foo2_ version _3.2.1_, choose the _Apache License 2.0_ from the multi-license. When foss_finder parses this field, it checks that the license of the package is actually a multi-license and that the license provided in the `"multi-license-selection"` field is part of this multi-license. (You can tell that both these requirements are satisfied because _Foo2_ version _3.2.1_ was actually added through `"add-packages"`.)

For each field, every object in the array must have an `"owner"` (the person who added the object to the configuration file). Besides, it must also have a `"package"` field with the name of the pacakge. The `"version"` field is optional: if it's not specified, then foss_finder assumes the modification is relevant for all versions of the package.

### Global user defined information

There is a feature to avoid writing the same configuration in every repository of an organization. Just like you can add _.foss.json_ at the root of a repository, you can add _.foss.global.json_ in the directory where you launch the script (same directory as the INI configuration file _.foss_finder_). Its fields and constraints are exactly the same as the ones of _.foss.json_, except that they are global. It's the same as adding these fields to _.foss.json_ for every repository that is scanned by foss_finder.

It is possible to have conflicts between _.foss.global.json_ and a given _.foss.json_. In that event, priority is given to _.foss.json_. Indeed, for each package that is added or overwitten, foss_finder first looks at _.foss.json_ and if it's not found there, then it looks at _.global.json_.

## Development

### Architecture of the project's directories

```
foss_finder
├── config                 -> global config folder of the script
│   ├── config.py          -> get variables from INI config file and define other variables
│   └── strings.py         -> strings that are used in many locations in the code
├── scripts                -> entry point
│   └── foss_finder_cli.py -> main script to recursively look for requirements files
├── utils                  -> folders containing useful classes and functions for the script
│   ├── csv                -> everything related to csv editing
│   │   └── csv.py         -> simple function to write a line in a csv file
│   ├── parsers            -> parsers to extract dependencies details from files
│   │   ├── npm_parser.py  -> parser to get NPM packages info from package.json and bower.json
│   │   └── pypi_parser.py -> parser to get Python packages info from files like requirements.txt
│   ├── tracker            -> a tracker should keep track of the info of packages and other stats
│   │   ├── tracker.py     -> class implementing a tracker to keep info and stats for projects
│   │   └── project.py     -> class implementing a project and its operations: add packages, etc.
│   ├── user_defined_info  -> contains classes and functions to support user-defined information (UDI)
│   │   ├── fields         -> contains classes implementing the supported fields of the UDI file
│   │   └── base.py        -> class to process fields, validate data of the UDI file, etc.
│   └── validators         -> validators raise exceptions when a package's info doesn't pass a check
│       ├── base.py        -> abstract class for checks and base class for check exceptions
│       └── gpl_check.py   -> check that a package is not licensed under a GPL-like license
└── .foss_finder           -> INI configuration file that should be modified by the user
```
