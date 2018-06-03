#!python
#-- setup.py -- ripsaw

'''
Ripsaw
==========

Cut logs into bits

'''

#----------------------------------------------------------------------------------------------#

from setuptools import setup
from ripsaw.__setup__ import options

setup( **options, long_description=__doc__)


#----------------------------------------------------------------------------------------------#
