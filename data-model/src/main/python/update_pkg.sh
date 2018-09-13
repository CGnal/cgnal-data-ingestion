#!/usr/bin/env bash

python setup.py sdist
source ~/venvs/cgnal-data-ingestion/bin/activate
pip install -I --upgrade dist/cgnal-core-1.0.0.tar.gz
