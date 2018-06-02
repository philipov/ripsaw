@setlocal
@ECHO off
cls
rem ---------------------------------

set THIS_PATH=%~dp0
set PROJECT_PATH=%THIS_PATH%..\..

set TESTS_PATH=%PROJECT_PATH%\tests
set TMP_PATH=%TESTS_PATH%\__tmp__

set PYTHONPATH=%TESTS_PATH%;%PROJECT_PATH%;%PYTHONPATH%
@pushd %PROJECT_PATH%


rem ---------------------------------
where python
rem mkdir %TMP_PATH%

py.test %TESTS_PATH%\%* --basetemp=%TMP_PATH%
call sh\win\clean.bat


rem ---------------------------------
@popd
@endlocal
