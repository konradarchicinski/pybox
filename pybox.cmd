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
IF "%args%"=="ii" (GOTO python_interpreter)
IF "%args%"=="CreateBox" (GOTO create_box)
IF "%args%"=="CreateTask" (GOTO create_task) ELSE (GOTO run_task)

:python_interpreter
CALL ipython
GOTO execute

:create_box
ECHO.
SET /p box_args=CreateBox:
ECHO.
CALL python -m pybox.create_box %box_args%
GOTO execute

:create_task
ECHO.
SET /p task_args=CreateTask:
ECHO.
CALL python -m pybox.create_task %task_args%
GOTO execute

:run_task
CALL python -m pybox.run_task "%args%"
GOTO execute
