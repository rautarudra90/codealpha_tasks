@echo off
ECHO ============================================
ECHO  EDA Analytics Suite - Windows Setup and Run
ECHO ============================================

python -m pip install --upgrade pip
pip install -r requirements.txt

ECHO.
ECHO Running EDA pipeline...
python main.py --all

ECHO.
ECHO Done. Check the output\charts and output\reports folders.
ECHO To launch the interactive dashboard instead, run: streamlit run dashboard.py
pause
