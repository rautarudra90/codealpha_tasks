@echo off
ECHO ================================================
ECHO  Data Visualization Project - Windows Setup
ECHO ================================================

python -m pip install --upgrade pip
pip install -r requirements.txt

ECHO.
ECHO Choose an option:
ECHO 1. Generate static charts + data story (python main.py)
ECHO 2. Launch interactive Streamlit dashboard
SET /P choice="Enter 1 or 2: "

IF "%choice%"=="2" (
    streamlit run dashboard.py
) ELSE (
    python main.py
)

pause
