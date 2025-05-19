from flask import Flask, render_template, request, redirect, url_for
import csv

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
            flashcards.append({
                'question': q,
                'answer': a,
                'module': m
            })
    return flashcards

@app.route('/')
def index():
    flashcards = load_flashcards()
    return render_template('index.html', flashcards=flashcards)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
