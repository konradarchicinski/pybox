@ECHO OFF
CALL conda activate PyBox
ECHO.
ECHO Welcome to PyBox.
ECHO. 
ECHO To execute the task, pass its name.
ECHO If you want to know more about certain task, type its name and add `-ti`.
ECHO If you want to use an interactive interpreter type `ii`.
ECHO For more information type `-h`.
ECHO.

:execute
ECHO.
SET /p args=Task:
ECHO.
IF "%args%"=="exit" EXIT 
IF "%args%"=="ii" (GOTO python_interpreter) ELSE (GOTO run_task)

:python_interpreter
CALL ipython
GOTO execute

:run_task
CALL python -m pybox.run_task "%args%"
GOTO execute
