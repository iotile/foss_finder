# FOSS Finder

A Python script to look for the dependencies used in the repositories of a GitHub organization.

## Installation

When it comes to using Python packages, it is always recommended you use a Python Virtual Env. Using Python 3, you can simply do:

```
python3 -m venv  ~/.virtualenv/foss_finder
```

Once the virtual environment is set up, simply install the dependencies with:

```
pip install -U pip
pip install -r requirements.txt
```

## How to use the script

### Basic usage

The script is fairly easy to use but if you need any help, you can run:

```
python github_find_foss.py -h
```

The standard way to run the script is to get an access token for your GitHub organization, then run:

```
python github_find_foss.py -t <your_access_token> <name_of_your_organization>
```

Alternatively, you can directly use your GitHub username to login:

```
python github_find_foss.py -u <your_username> <name_of_your_organization>
```

### Other options

The above commands run the script on all the repositories of the organization. If you want to process a single repository, you can do so by adding `--project <name_of_your_repository>`.

By default, the reports are stored in csv format in a directory named _out_. The names of the reports are _<name_of_your_repository>.csv_. You can change the directory where these csv files are saved by adding `-o <relative_path_of_directory>`.

By default, the script only looks for production dependencies. If you wish to look for development and build dependencies too, then you can add `--dev`. Production vs development dependencies are defined by a configuration file (see below).

Finally, you can add `--debug` to enable debug mode.

### Configuration

The main config file for the script is `/config/config.py`.

The `FIELDS` value defines the structure of the output csv files.

The `INI_PATH` value defines the path of the INI configuration file, which is the file you want to change to get the script doing what you want.

By default, this INI configuration file is named *.foss_finder*. It contains three sections and several keys.

#### NPM sections

The keys define the sections that are looked for inside _package.json_ and _bower.json_ (NPM dependencies). `npm_prod` defines the sections which correspond to production and `npm_dev` defines the sections which correspond to development (they are looked for when you use the `--dev` argument).

#### Python files

The keys define the files that are looked for (Python dependencies). `py_prod` corresponds to the production files and `py_dev` corresponds to the development files.  
The files that are looked for are those whose name contains the name of one of the files defined here. For instance, if `py_prod` contains _/requirements.txt_, then the following files will match: _/requirements.txt_, _/somefolder/requirements.txt_. So, be careful to include the '/' because if it contained _requirements.txt_, then _dev_requirements.txt_ would match!

#### Ignored repositories

`ignored_repos` is simply the list of the repositories which should be ignored. If a repo contains no dependency but does have multiple different folders, you want to include it here so that the script doesn't waste a lot of time trying to find dependencies in all these folders.

## Development

### Architecture of the project's directories

```
.
├── config
│   ├── config.py          -> configuration of the fields in csv files
│   └── strings.py         -> strings that are used in many locations in the code
├── utils
│   ├── csv                -> everything related to csv editing
│   │   └── csv.py         -> simple function to write a line in a csv file
│   ├── parsers            -> parsers to extract dependencies details from files
│   │   ├── npm_parser.py  -> parser to get NPM packages info from package.json and bower.json
│   │   └── pypi_parser.py -> parser to get Python packages info from files like requirements.txt
│   └── tracker            -> a tracker should keep track of the info of packages and other stats
│       └── tracker.py     -> class implementing a tracker to keep info and stats
├── .foss_finder           -> INI configuration file
└── github_find_foss.py    -> main script to recursively look for requirements files
```
