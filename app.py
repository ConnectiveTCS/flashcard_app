from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import csv
import tempfile
import shutil
import os, requests, io
from your_text_utils import extract_text, chunk_text

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Configuration
PIPEDREAM_URL = "https://eon3qzp0ncyhk31.m.pipedream.net" # Replace with your Pipedream URL for development
# Example: PIPEDREAM_URL = "https://eoy872aby7m89h7.m.pipedream.net"

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


@app.route("/upload", methods=["POST"])
def upload():
    # Check if we're getting a file or text input
    if 'file' in request.files and request.files['file'].filename:
        f = request.files.get("file")
        # 1) Extract raw text
        raw_text = extract_text(f)
    elif 'text' in request.form and request.form['text'].strip():
        # If text was provided directly
        raw_text = request.form['text']
    else:
        return jsonify({"error": "No file or text provided"}), 400

    # 2) Split into manageable chunks
    chunks = chunk_text(raw_text, max_tokens=3000)

    # Get the Pipedream URL from environment variable or fallback to the constant
    pipedream_url = os.environ.get("PIPEDREAM_TRIGGER_URL", PIPEDREAM_URL)
    
    if not pipedream_url:
        error_msg = """
        No Pipedream URL configured. Please do one of the following:
        1. Set the PIPEDREAM_TRIGGER_URL environment variable, or
        2. Update the PIPEDREAM_URL constant in the app.py file
        """
        return jsonify({"error": error_msg.strip()}), 500

    # 3) For each chunk, call Pipedream + OpenAI
    all_flashcards = []
    try:
        for chunk in chunks:
            resp = requests.post(
                pipedream_url,
                json={"content": chunk}
            )
            resp.raise_for_status()
            data = resp.json()
            # assume Pipedream returns {"flashcards": "…markdown table…"}
            all_flashcards.append(data["flashcards"])
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {str(e)}"}), 500

    # 4) Combine & send back
    combined = "\n\n".join(all_flashcards)
    return jsonify({"flashcards": combined})

if __name__ == '__main__':
    images_dir = os.path.join('static', 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        
    app.run(debug=True, host="0.0.0.0")
