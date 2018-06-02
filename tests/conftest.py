#!python
#-- conftest

"""
powertest
"""

import pytest

from datetime import datetime
from pathlib import Path

import shutil
import os

import time
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('conftest')

#----------------------------------------------------------------------------------------------#

def prepare_testdata( path_destination:Path ):
    testdata_source = Path(__file__).parents[0] / 'testdata'
    testdata_temp   = path_destination / 'testdata'
    shutil.copytree( str(testdata_source), str(testdata_temp) )

    # time.sleep(1)
    return testdata_temp


@pytest.fixture(scope="session")
def path_testdata( tmpdir_factory ):
    ### Setup
    testenv_path = None
    for value in range(0,10000):
        try:
            testenv_path = Path( str( tmpdir_factory.mktemp( 'env' ) ) )
            break
        except PermissionError:
            pass
        except FileNotFoundError:
            pass
    assert testenv_path is not None

    # copy test data to temp directory
    testdata_temp = prepare_testdata( testenv_path )

    # construct backup path for teardown
    test_start = datetime.now( )
    test_start_string = test_start.strftime("%Y%m%d%H%M%S")
    backup_path = testenv_path.parents[1] / '__backup__' / test_start_string
    print("Path Testenv:", testenv_path)
    print("Path Backup: ", backup_path)

    os.chdir( str(testdata_temp) )
    yield testdata_temp

    ### Teardown
    shutil.copytree( str(testenv_path), str(backup_path) )


#----------------------------------------------------------------------------------------------#
