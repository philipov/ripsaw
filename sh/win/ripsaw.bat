@setlocal
@ECHO off
rem ---------------------------------

set THIS_PATH=%~dp0
set PROJECT_PATH=%THIS_PATH%..\..
set PROJECT_NAME=ripsaw

set PYTHONPATH=%PROJECT_PATH%;%PYTHONPATH%
@pushd %PATH_PROJECT%


rem ---------------------------------
where python

set CMD=python -m %PROJECT_NAME% %*
echo "CMD" %CMD%
%CMD%

rem ---------------------------------
@popd
@endlocal
