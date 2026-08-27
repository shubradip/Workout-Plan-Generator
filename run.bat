@echo off
set PATH=C:\Users\user\anaconda3\Library\bin;%PATH%
set PYTHONPATH=%~dp0
call "%~dp0.venv\Scripts\activate.bat"
streamlit run "%~dp0app.py"
pause
