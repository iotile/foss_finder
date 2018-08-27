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

The script is fairly easy to use. You just have to get an access token for your GitHub organization, then run:

```
python github_find_foss.py -t <your_access_token> <name_of_your_organization>
```

You can add `--debug=True` to enable debug mode.
