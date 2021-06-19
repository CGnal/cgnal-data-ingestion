#!/usr/bin/env bash

cd cgnal/tests
python -m xmlrunner discover -v -o /tmp/tests-reports/cgnal-core/package

cd ../../