@echo off
:: Script untuk Windows Task Scheduler
:: Jalankan otomatis setiap tanggal 1, pukul 08:00

cd /d "%~dp0"
python main.py >> "%~dp0..\logs\run_log.txt" 2>&1
