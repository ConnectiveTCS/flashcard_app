from flask import Flask, render_template, request, redirect, url_for
import openpyxl

app = Flask(__name__)

def load_flashcards(filename="flashcards.xlsx"):
    workbook = openpyxl.load_workbook(filename)
    sheet = workbook.active
    flashcards = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        question, answer = row
        if question and answer:
            flashcards.append({"question": question, "answer": answer})
    return flashcards

@app.route('/')
def index():
    flashcards = load_flashcards()
    return render_template('index.html', flashcards=flashcards)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
