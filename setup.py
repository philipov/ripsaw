#!python
#-- setup.py -- ripsaw

#----------------------------------------------------------------------------------------------#

from setuptools import setup
from ripsaw.__setup__ import options
import os

with open( os.path.join( os.path.dirname( __file__ ), 'DESCRIPTION.rst' ) ) as r_file :
    long_description = r_file.read()

setup( **options, long_description=long_description )


#----------------------------------------------------------------------------------------------#
