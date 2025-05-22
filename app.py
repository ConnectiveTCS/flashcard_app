from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import csv
import os
import tempfile
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_flashcards():
    flashcards = []
    with open('flashcards.csv', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            q = row[0]
            a = row[1] if len(row) > 1 else ''
            m = row[2] if len(row) > 2 else None
            l = row[3] if len(row) > 3 else None
            
            if l and not (l.startswith('http://') or l.startswith('https://')):
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

@app.route('/admin')
def admin():
    flashcards = load_flashcards()
    return render_template('admin.html', flashcards=flashcards)

@app.route('/add_flashcard', methods=['POST'])
def add_flashcard():
    question = request.form['question']
    answer = request.form['answer']
    module = request.form['module']
    
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = f'/static/images/{filename}'
    
    with open('flashcards.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([question, answer, module, image_path])
    
    return redirect(url_for('admin', success=True))

@app.route('/edit_flashcard/<int:index>', methods=['POST'])
def edit_flashcard(index):
    flashcards = load_flashcards()
    
    if index < 0 or index >= len(flashcards):
        return jsonify({"success": False, "message": "Invalid flashcard index"}), 400
    
    question = request.form['question']
    answer = request.form['answer']
    module = request.form['module']
    
    image_path = flashcards[index]['link']
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = f'/static/images/{filename}'
    
    temp_fd, temp_path = tempfile.mkstemp(text=True)
    try:
        with os.fdopen(temp_fd, 'w', newline='', encoding='utf-8') as temp_file:
            writer = csv.writer(temp_file)
            
            with open('flashcards.csv', 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for i, row in enumerate(reader):
                    if i == index:
                        writer.writerow([question, answer, module, image_path])
                    else:
                        writer.writerow(row)
        
        shutil.move(temp_path, 'flashcards.csv')
        return redirect(url_for('admin', edited=True))
    
    except Exception as e:
        os.unlink(temp_path)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/delete_flashcard/<int:index>', methods=['POST'])
def delete_flashcard(index):
    flashcards = load_flashcards()
    
    if index < 0 or index >= len(flashcards):
        return jsonify({"success": False, "message": "Invalid flashcard index"}), 400
    
    temp_fd, temp_path = tempfile.mkstemp(text=True)
    try:
        with os.fdopen(temp_fd, 'w', newline='', encoding='utf-8') as temp_file:
            writer = csv.writer(temp_file)
            
            with open('flashcards.csv', 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for i, row in enumerate(reader):
                    if i != index:
                        writer.writerow(row)
        
        shutil.move(temp_path, 'flashcards.csv')
        return redirect(url_for('admin', deleted=True))
    
    except Exception as e:
        os.unlink(temp_path)
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    images_dir = os.path.join('static', 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        
    app.run(debug=True, host="0.0.0.0")
