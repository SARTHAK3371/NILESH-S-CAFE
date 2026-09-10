@echo off
echo ========================================
echo   Cafe Management System
echo   Developed by: Nilesh Shelke
echo ========================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting server...
echo Open browser at: http://127.0.0.1:5000
echo.
echo Login: admin / admin123
echo.
python app.py
pause
