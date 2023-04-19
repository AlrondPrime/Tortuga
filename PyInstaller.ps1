./venv/Scripts/pyinstaller.exe --windowed `
 --icon "../../resources/Shipwreck.ico" `
 --onefile `
"./src/Main.py" `
--name "Tortuga" `
--distpath "." `
--specpath "./build/Tortuga" `
--add-data "../../venv/Lib/site-packages/pywin32_system32/pywintypes*.dll;."
pause