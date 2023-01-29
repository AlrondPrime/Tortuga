./venv/Scripts/pyinstaller.exe --windowed `
 --icon "./resources/Shipwreck.ico" `
 --onefile `
"./src/Main.py" `
--name "Tortuga" `
--distpath "." `
--add-data "./venv/Lib/site-packages/pywin32_system32/pywintypes311.dll;."
