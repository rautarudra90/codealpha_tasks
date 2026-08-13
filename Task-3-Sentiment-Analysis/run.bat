@echo off
ECHO ==================================================
ECHO  Sentiment Analysis Project - Windows Setup & Run
ECHO ==================================================

python -m pip install --upgrade pip
pip install -r requirements.txt

ECHO.
ECHO Running sentiment analysis pipeline...
python main.py

ECHO.
ECHO Done. Check the output folder for the report, charts, and results CSV.
pause
