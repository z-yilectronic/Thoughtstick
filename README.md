

# A catch & freeze note-taker. 
'Send' thoughts instantly, and then hide them for hours.

# Quick start
Run in CMD:
```bash
python main.py
```
Package this script into a standalone Windows executable using a clean environment:
```bash
python -m venv venv_pack
.\venv_pack\Scripts\activate
pip install PyQt6 pyinstaller
pyinstaller --noconsole --onefile --name="thoughtstick" main.py
```

# Talk..

I often have pop-up thoughts, ranging from lunch, pets and fanart to some "ah, it might be useful.." idea, unfortunately, during working. 
I hope to simply throw these fluffy ideas into a place for later exploration, allowing me to stay focused on my current flow.   

This tool is built with the Python package PyQt6, with assistance from Gemini-3. Great thanks to the vast amount of open-source code that modern AI models are built upon.

Future Features to be added, hopefully: Shortcut for Exiting, Custom Timer 
