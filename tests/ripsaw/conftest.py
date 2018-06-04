#-- conftest.unit

"""
fixtures for module unit tests
"""

import pytest
import time
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('conftest.unit')


#----------------------------------------------------------------------------------------------#

@pytest.fixture( scope="session" )
def path_script(path_testdata):
    return path_testdata/'monitor.py'


#----------------------------------------------------------------------------------------------#



#----------------------------------------------------------------------------------------------#
