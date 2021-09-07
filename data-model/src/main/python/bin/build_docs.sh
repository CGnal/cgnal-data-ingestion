#!/usr/bin/env bash

sphinx-build -b html "${PROJECT_DIR}/sphinx/source" "${PROJECT_DIR}/docs"
touch "${PROJECT_DIR}/docs/.nojekyll"