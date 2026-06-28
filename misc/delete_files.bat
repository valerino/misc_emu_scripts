@echo off
setlocal EnableDelayedExpansion

:: Parse arguments
set "DRY_RUN=false"
set "TARGET_DIR="
set "SHOW_HELP=false"

:parse_args
if "%~1"=="" goto check_args
if /I "%~1"=="--help" (
    set "SHOW_HELP=true"
    shift
    goto parse_args
)
if /I "%~1"=="--dry-run" (
    set "DRY_RUN=true"
    shift
    goto parse_args
)
if not defined TARGET_DIR (
    set "TARGET_DIR=%~1"
)
shift
goto parse_args

:check_args
if "%SHOW_HELP%"=="true" goto show_help
if not defined TARGET_DIR (
    echo Error: No directory specified.
    echo.
    goto show_help
)

if not exist "%TARGET_DIR%\" (
    echo Error: '%TARGET_DIR%' is not a valid directory.
    exit /b 1
)

if "%DRY_RUN%"=="true" (
    echo === DRY RUN MODE - No files will be deleted ===
    for /r "%TARGET_DIR%" %%F in (*) do (
        if not exist "%%F\" (
            echo %%F
        )
    )
    echo === End of dry run ===
) else (
    for /r "%TARGET_DIR%" %%F in (*) do (
        if not exist "%%F\" (
            del /f /q "%%F"
        )
    )
    echo All files deleted from '%TARGET_DIR%' and its subdirectories.
)
exit /b 0

:show_help
echo Usage: %~nx0 [OPTIONS] ^<directory^>
echo.
echo Delete all files recursively while preserving directory structure.
echo.
echo Options:
echo   --dry-run    Preview files that would be deleted without actually
echo                deleting them. Prints the full path of each file.
echo   --help       Display this help message and exit.
echo.
echo Examples:
echo   %~nx0 C:\path\to\directory
echo   %~nx0 --dry-run C:\path\to\directory
echo   %~nx0 --help
exit /b 0
