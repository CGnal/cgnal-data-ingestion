#!/usr/bin/env bash

cd tests
python -m xmlrunner discover -v -o /tmp/tests-reports/cgnal-core/package
cd ../