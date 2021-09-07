# Core Package

Package with core abstraction developed by CGnal team

### Notes
This library is thought to be run with [pre-commit](https://pre-commit.com/) and [pip-tools](https://github.com/jazzband/pip-tools).
Follow the subsequent procedure to correctly configure the local repository for development. From root folder run:
1. `pip install -r requirements/requirements_dev.txt` install development requirements
2. `bash update_pkg.sh` to install current development version of cgnal-analytics
3. `pre-commit install` to configure pre-commit for current folder

Optionally, to automate pre-commit configuration for future repos using it, you can run also
4. `git config --global init.templateDir ~/.git-template` to set the templateDir used when cloning a repository
5. `pre-commit init-templatedir ~/.git-template` to add the pre-commit hook to templateDir that enables any newly cloned repository to have pre-commit automatically set up

This library collects its requirements in the *"requirements"* folder.
Requirements come from two files:
1. *setup.py* file must contain **only direct requirements** needed to install and run the package. **These requirements should be open** with minimum version corresponding to the minimum working version.
2. *requirements/requirements.in* must contain **only direct requirements** needed to run the package in development environment (i.e. all those dependencies that are not strictly required to run the package but are still useful during its development). This requirements can be both open or closed.

**Other files in *"requirements"* folder must not be modified by hand**, they will be automatically updated by the pre-commit hook defined in .pre-commit-config.yaml at each commit that modifies setup.py or requirements/requirements.in

To install dependencies it is advisabile to use `pip-sync` instead of simple `pip install -r FILENAME`. This command allows to keep the environment clean, uninstalling dependencies not declared in the target file (and thus not needed) and also allows installing dependencies syncing more files using `pip-sync requirements/requirements.txt requirements/requirements_dev.txt`

## Data Model

Implements a library for the data domain model to be used in the ingestion pipelines

It represents the following data models

* Document


## Changelog

1.0.1 Refactor packages (for document models) 