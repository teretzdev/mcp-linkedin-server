@echo off
echo ========================================
echo LinkedIn Job Hunter Test Suite
echo ========================================
echo.

if "%1"=="" (
    echo Usage: run_tests.bat [command]
    echo.
    echo Available commands:
    echo   install    - Install test dependencies
    echo   setup      - Setup test environment
    echo   unit       - Run unit tests
    echo   integration - Run integration tests
    echo   browser    - Run browser tests
    echo   performance - Run performance tests
    echo   security   - Run security tests
    echo   frontend   - Run frontend tests
    echo   all        - Run all tests
    echo   coverage   - Generate coverage report
    echo   lint       - Run linting
    echo   typecheck  - Run type checking
    echo   interactive - Run interactive mode
    echo.
    echo Example: run_tests.bat unit
    goto :eof
)

if "%1"=="interactive" (
    python run_tests.py
) else (
    python run_tests.py %1
)

echo.
echo Test execution completed.
pause 