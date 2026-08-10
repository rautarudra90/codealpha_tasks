#!/usr/bin/env bash
set -e

echo "============================================"
echo " EDA Analytics Suite - Setup and Run"
echo "============================================"

python3 -m pip install --upgrade pip
pip3 install -r requirements.txt

echo
echo "Running EDA pipeline..."
python3 main.py --all

echo
echo "Done. Check the output/charts and output/reports folders."
echo "To launch the interactive dashboard instead, run: streamlit run dashboard.py"
