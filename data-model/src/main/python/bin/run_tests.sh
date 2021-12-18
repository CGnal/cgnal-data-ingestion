#!/usr/bin/env bash

(
cd tests || exit 1
python -m xmlrunner discover -v -o /tmp/tests-reports/cgnal-core/package
cd ..
mypy --install-types --non-interactive --follow-imports silent cgnal tests
)
