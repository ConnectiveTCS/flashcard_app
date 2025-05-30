# Flashcards Admin

  

A simple Flask web application for creating, editing, deleting, and AI-generating study flashcards stored in CSV files.

  

## Features

  

- Add, edit, and delete flashcards via a web UI

- Persist flashcards in `flashcards.csv` (with automatic backups to `flashcards_backup.csv`)

- Generate flashcards from uploaded PDF/DOCX or pasted text using the OpenAI API

- Uses TailwindCSS + Flowbite for styling

  

## Project Structure

  

```

├── app.py # Flask application

├── requirements.txt # Python dependencies

├── your_text_utils.py # Text extraction helpers

├── flashcards.csv # Primary flashcard store (question,answer,module)

├── flashcards_backup.csv # Backup store

├── static/
	│ 
	└── images/ # Uploaded or associated images

├── templates/
	│ 
	└── index.html # Public flashcard view
	│
	└── admin.html # Admin interface (add/edit/delete/AI-gen)

```


## Prerequisites

- Python 3.7+

- pip

  

## Installation

  

1. Clone this repo

2. (Optional) Create and activate a virtual environment

3. Install dependencies:

````shell

pip install -r requirements.txt

````

  

4. Set your OpenAI API key:

  

```shell

export OPENAI_API_KEY="sk-…"

```

  

## Running

  

Start the server in development mode:

  

````shell

python  app.py

````

  

By default it listens on `http://0.0.0.0:5000/`.

  

- Browse `/` to view flashcards

- Browse `/admin` to manage flashcards

  

## Usage

  

### Adding Flashcards

  

- In **Admin** view, fill out **Question**, **Answer**, **Module**, optionally upload an image, then click **Add Flashcard**.

  

### AI-Powered Generation

  

1. In **Admin**, under **Generate Flashcards with AI**, upload a PDF/DOCX or paste text.

2. Click **Generate Flashcards**; AI-parsed flashcards appear in a modal.

3. Review and click **Save Flashcards** to add them to your collection.

  

### 📄 CSV Format

  

Flashcards are stored in `flashcards.csv` with the following structure:

  

```csv

Question,Answer,Module

"What is Python?","Python is a high-level programming language.","Programming Basics"

"Define variables in Python","Variables are containers for storing data values.","Programming Basics"

"What is a function?","A reusable block of code that performs a specific task.","Functions"

```

  

>  **Note:** Fields containing commas or line breaks must be properly quoted.

  

### 🛠️ Utilities

  

The project includes helpful utility files:

  

-  `your_text_utils.py`: Helper functions that extract text from:

- PDF (`.pdf`) documents

- Word (`.docx`) documents

- Supports multi-page documents and various formatting

  

### 📝 License

  

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

```