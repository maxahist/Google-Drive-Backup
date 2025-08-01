@echo off
:check_net
ping -n 1 8.8.8.8 >nul || (
    timeout /t 30 /nobreak
    goto :check_net
)

@echo off
chcp 65001 > nul
set PYTHONIOENCODING=UTF-8
setlocal EnableDelayedExpansion

title Запуск скрипта с поддержкой кириллицы
color 0a

:: Автоматическое определение путей
set "ROOT_DIR=%~dp0"
set "VENV_DIR=%ROOT_DIR%venv"
set "SCRIPT_PATH=%ROOT_DIR%docs.py"
set "SCRIPT_PATH2=%ROOT_DIR%d_to_ftp.py"

echo [1/5] Настройка кодировки для кириллицы...
echo ----------------------------------------

:: Проверка существования venv
if not exist "%VENV_DIR%" (
    echo Ошибка: Виртуальное окружение не найдено!
    echo Путь: %VENV_DIR%
    pause
    exit /b 1
)

:: Активация виртуального окружения
echo [2/5] Активация виртуального окружения...
call "%VENV_DIR%\Scripts\activate.bat"

:: Проверка Python
echo [3/5] Проверка среды Python...
python -c "print('✅ Проверка кириллицы: Привет, мир!')" || (
    echo Ошибка: Проблема с Python или кодировкой
    pause
    exit /b 1
)

:: Запуск скрипта
echo [4/5] Запуск скрипта на скачивание...
echo ========================================
python "%SCRIPT_PATH%"
set EXIT_CODE=!errorlevel!
echo ========================================

:: Итоги выполнения
if !EXIT_CODE! equ 0 (
    echo Скрипт успешно завершен ✓
) else (
    echo ОШИБКА выполнения ✗ Код: !EXIT_CODE!
	 exit /b 1)		


:: Запуск скрипта
echo [5/5] Запуск скрипта на загрузку...
echo ========================================
python "%SCRIPT_PATH2%"
set EXIT_CODE=!errorlevel!
echo ========================================

:: Деактивация venv
call deactivate

:: Итоги выполнения
if !EXIT_CODE! equ 0 (
    echo Скрипт успешно завершен ✓
) else (
    echo ОШИБКА выполнения ✗ Код: !EXIT_CODE!
)

pause
exit /b !EXIT_CODE!