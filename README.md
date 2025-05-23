# flashcard_app

## Overview
flashcard_app is a web-based flashcard study tool built with Flask (Python) on the backend and Vite + Tailwind CSS on the frontend. It reads your flashcards from an Excel file and presents them in an interactive 3D-flip interface.

## Key Features
- 3D flip animation for question/answer cards  
- Bookmark cards for later review  
- Mark cards as correct or incorrect  
- Index view with filtering by “Module”  
- Responsive design using Tailwind CSS & Flowbite  
- Simple Excel-based content management

## Prerequisites
- Python 3.7+  
- pip (Python package manager)  
- Node.js 14+ & npm (for frontend build)

## Installation

1. Clone the repo  
   ```powershell
   git clone https://github.com/ConnectiveTCS/flashcard_app.git C:\Flashcard_App\
   cd C:\Flashcard_App\
   ```

2. Setup Python environment  
   ```powershell
   python -m venv venv
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # (or in cmd.exe: venv\Scripts\activate.bat)
   pip install -r requirements.txt
   ```

3. Run the app  
   ```powershell
   cd .\dist
   .\app.exe
   ```

## Usage

1. Prepare your flashcards in `flashcards.xlsx` at the project root.  
   - Columns: `Question`, `Answer`, optional `Module`  
2. Start the Flask server:  
   ```bash
   python app.py
   ```  
3. Open your browser at `http://localhost:5000`

## File Structure
```
d:\Studies\STADIO\FLASHCARDS
│
├─ app.py                   # Flask backend
├─ flashcards.xlsx          # Excel source data
│
├─ templates
│   └─ index.html           # Main UI template
│
├─ static
│   ├─ style.css            # custom overrides
│   └─ index.css            # compiled Tailwind CSS
│
├─ package.json             # npm deps & scripts
├─ tailwind.config.js
├─ postcss.config.js
├─ vite.config.js
│
├─ src
│   ├─ input.css            # Tailwind imports
│   └─ output.css           # build artifact (optional)
└─ README.md                # this document
```

## Customization Tips
- Tailor colors, fonts, and spacing in `tailwind.config.js`.  
- Add new modules by simply tagging rows in `flashcards.xlsx`.  
- Extend `templates/index.html` with additional controls or views.  
- Modify animations or behavior in `static/style.css` or via Flowbite utility classes.  
- For production, consider using `npm run build -- --mode production` and serve static files via a CDN or reverse proxy.
