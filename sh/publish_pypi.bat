@setlocal
@ECHO off

set THIS_PATH=%~dp0
set PROJECT_PATH=%THIS_PATH%..
set PIP_CONFIG_FILE=C:\dev\secrets\pip.ini
@pushd %PROJECT_PATH%

rem -- ToDo: macro to obtain __version__

twine upload %PROJECT_PATH%\dist\ripsaw-0.0.7.tar.gz --comment "fix setup.py and some polish"

@popd
@endlocal
