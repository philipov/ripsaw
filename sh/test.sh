#!/usr/bin/env bash

###########################
export THIS_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PROJECT_PATH="${THIS_PATH}/.."
export TESTS_PATH="${PROJECT_PATH}/tests"
export TMP_PATH="${TESTS_PATH}/__tmp__"

export PYTHONPATH="${TEST_PATH}:${PROJECT_PATH}:${PYTHONPATH}"
pushd ${PROJECT_PATH}

###########################

which python

CMD="py.test ${TESTS_PATH}/$* --basetemp=${TMP_PATH}"
echo ${CMD}
${CMD}

###########################
popd
