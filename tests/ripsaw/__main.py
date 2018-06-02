

'''
integration tests for main program
'''

import shlex
import pytest
import os
from click.testing import CliRunner

#----------------------------------------------------------------------------------------------#

params_argv = list()
params_argv.append( shlex.split('echo import time; time.sleep(5) | python -') )
params_argv.append( shlex.split('echo ECHO ECHO ECHO') )

@pytest.mark.parametrize("argv", params_argv)
def test__main( path_env00, argv ) :

    from smash.__main__ import console

    os.chdir( str( path_env00) )

    runner = CliRunner( )
    result = runner.invoke( console, argv )


    # assert False


#----------------------------------------------------------------------------------------------#


