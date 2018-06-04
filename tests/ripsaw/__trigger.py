#-- tests.ripsaw.trigger

''' unit tests
'''

import pytest

#----------------------------------------------------------------------------------------------#

#######################
def test__trigger():
    from ripsaw.trigger import Trigger

    t = Trigger()

#######################
def test__regex():
    from ripsaw.trigger import Regex

    t = Regex('.*')

#######################
def test__and():
    from ripsaw.trigger import And

    t = And()

#######################
def test__Or():
    from ripsaw.trigger import Or

    t = Or()


#----------------------------------------------------------------------------------------------#


