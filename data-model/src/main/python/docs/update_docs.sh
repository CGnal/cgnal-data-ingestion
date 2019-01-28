#!/usr/bin/env bash

sphinx-apidoc -f -o source/api -d 7 ../cgnal
python process_api_rst.py