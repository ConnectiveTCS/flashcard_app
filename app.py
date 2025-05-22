from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

def load_flashcards():
    flashcards = []
    with open('flashcards.csv', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            # unpack with optional module column
            q = row[0]
            a = row[1] if len(row) > 1 else ''
            m = row[2] if len(row) > 2 else None
            l = row[3] if len(row) > 3 else None
            
            # Ensure image links are correctly formatted for Flask
            if l and not (l.startswith('http://') or l.startswith('https://')):
                # If it's a relative path, ensure it points to static directory
                if l.startswith('/'):
                    if not l.startswith('/static'):
                        l = f"/static{l}"
            
            flashcards.append({
                'question': q,
                'answer': a,
                'module': m,
                'link': l,
            })
    return flashcards

@app.route('/')
def index():
    flashcards = load_flashcards()
    return render_template('index.html', flashcards=flashcards)

if __name__ == '__main__':
    # Ensure the static/images directory exists
    images_dir = os.path.join('static', 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        
    app.run(debug=True, host="0.0.0.0")
