@setlocal
@ECHO off
rem ---------------------------------

set THIS_PATH=%~dp0
set PROJECT_PATH=%THIS_PATH%..
set PROJECT_NAME=ripsaw

set PYTHONPATH=%PROJECT_PATH;%PYTHONPATH%
@pushd %PATH_PROJECT%


rem ---------------------------------

call sh\win\test
pip uninstall %PROJECT_NAME% --yes --verbose
pip install %PROJECT_PATH% --verbose


rem ---------------------------------
@popd
@endlocal
