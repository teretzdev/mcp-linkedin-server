@echo off
echo ========================================
echo LinkedIn Job Hunter Database Integration
echo ========================================
echo.

echo Installing database dependencies...
pip install sqlalchemy alembic

echo.
echo Initializing database...
python database_integration.py

echo.
echo Starting API bridge with database...
python api_bridge_with_database.py

pause 