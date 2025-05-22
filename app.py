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
PIPEDREAM_URL = "https://eoosvr9vgrfl7zj.m.pipedream.net" # Update with a working Pipedream endpoint
# If direct OpenAI access is needed for fallback
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "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")  # Configure your OpenAI API key here or via env var

# For debugging - set to True to print detailed API request info
DEBUG_MODE = True

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

@app.route("/extract-text", methods=["POST"])
def extract_text_endpoint():
    """Extract text from uploaded file and return it"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        text = extract_text(file)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_flashcards_with_openai(text):
    """Generate flashcards directly using OpenAI API as a fallback."""
    if not OPENAI_API_KEY:
        return "# OpenAI API Key Missing\n\nPlease set your OPENAI_API_KEY environment variable to use the direct OpenAI fallback."
    
    try:
        # Import OpenAI for the newer API format (v1.0.0+)
        import openai
        
        # Create client with API key
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Use the new chat completions format
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates educational flashcards from text."},
                {"role": "user", "content": f"Generate 5-10 flashcards in markdown format from this text. Format each flashcard with a question followed by the answer:\n\n{text}"}
            ],
            max_tokens=1000
        )
        
        # Access the content with the new response format
        return response.choices[0].message.content
    except ImportError:
        return "# OpenAI Library Error\n\nPlease install the OpenAI Python package: `pip install openai>=1.0.0`"
    except Exception as e:
        return f"# Error with OpenAI Fallback\n\nCould not generate flashcards using OpenAI: {str(e)}"

@app.route("/upload", methods=["POST"])
def upload():
    # Always expect text input now, not files
    if 'text' not in request.form or not request.form['text'].strip():
        return jsonify({"error": "No text provided"}), 400
    
    # Get the text from the form
    raw_text = request.form['text']

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

    # 3) For each chunk, call Pipedream + OpenAI with proper error handling
    all_flashcards = []
    pipedream_failed = False
    
    try:
        if DEBUG_MODE:
            print(f"Using Pipedream URL: {pipedream_url}")
        
        # Common headers for all requests
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Flashcards-App/1.0'
        }
        
        for i, chunk in enumerate(chunks):
            try:
                if DEBUG_MODE:
                    print(f"Processing chunk {i+1}/{len(chunks)} - Length: {len(chunk)} chars")
                
                if not pipedream_failed:
                    try:
                        # Format the request data
                        request_data = {"content": chunk}
                        
                        # Try with POST (this is most likely what Pipedream expects)
                        if DEBUG_MODE: 
                            print(f"Sending POST request to {pipedream_url}")
                        
                        resp = requests.post(
                            pipedream_url,
                            json=request_data,
                            headers=headers,
                            timeout=60  # Increase timeout to 60 seconds
                        )
                        
                        if DEBUG_MODE:
                            print(f"POST Response status: {resp.status_code}")
                            print(f"Response headers: {resp.headers}")
                            print(f"Response content: {resp.text[:200]}...")
                        
                        # Check for success
                        resp.raise_for_status()
                        
                        try:
                            data = resp.json()
                            
                            # Check if the expected key exists in the response
                            if "flashcards" not in data:
                                if DEBUG_MODE:
                                    print(f"Missing 'flashcards' field in response: {data}")
                                
                                # Try to use whatever we got back
                                if isinstance(data, dict):
                                    # Try to find any field that might contain our flashcards
                                    for key, value in data.items():
                                        if isinstance(value, str) and len(value) > 50:
                                            all_flashcards.append(value)
                                            break
                                    else:
                                        # If no suitable field found, fall back to OpenAI direct
                                        raise ValueError(f"API response missing 'flashcards' field: {data}")
                                else:
                                    raise ValueError(f"Unexpected response type: {type(data)}")
                            else:
                                all_flashcards.append(data["flashcards"])
                                
                        except (ValueError, KeyError) as e:
                            if DEBUG_MODE:
                                print(f"Error parsing response: {str(e)}")
                            
                            # Fall back to direct OpenAI
                            raise ValueError("Invalid response from Pipedream")
                            
                    except (requests.exceptions.RequestException, ValueError) as e:
                        # Pipedream failed, switch to direct OpenAI for all remaining chunks
                        if DEBUG_MODE:
                            print(f"Pipedream failed, switching to direct OpenAI: {str(e)}")
                        
                        pipedream_failed = True
                        # Continue to the OpenAI fallback below
                
                # If pipedream failed or we already had issues, use direct OpenAI
                if pipedream_failed:
                    if DEBUG_MODE:
                        print("Using direct OpenAI fallback")
                    
                    # Generate flashcards directly with OpenAI
                    flashcards = generate_flashcards_with_openai(chunk)
                    all_flashcards.append(flashcards)
                
            except Exception as e:
                import traceback
                error_detail = f"Error processing chunk {i+1}/{len(chunks)}: {str(e)}"
                if DEBUG_MODE:
                    print(f"CHUNK ERROR: {error_detail}")
                    print(traceback.format_exc())
                
                # Instead of failing completely, add an error message to the flashcards
                all_flashcards.append(f"# Error Processing This Section\n\n{error_detail}\n\nHere's the text that failed:\n\n{chunk[:200]}...")
                
        # If we have no valid flashcards at all, return an error
        if not all_flashcards:
            return jsonify({"error": "Failed to generate any flashcards. Please check your API configuration."}), 500
                
    except Exception as e:
        import traceback
        error_detail = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        if DEBUG_MODE:
            print(f"PROCESSING ERROR: {error_detail}")
        return jsonify({"error": f"Error processing text: {error_detail}"}), 500

    # 4) Combine & send back
    combined = "\n\n".join(all_flashcards)
    return jsonify({"flashcards": combined})

@app.route("/save_generated_flashcards", methods=["POST"])
def save_generated_flashcards():
    """Save multiple flashcards from generated content"""
    try:
        data = request.json
        if not data or not data.get('flashcards'):
            return jsonify({"error": "No flashcards provided"}), 400
            
        flashcards = data.get('flashcards')
        count = 0
        
        with open('flashcards.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            for card in flashcards:
                question = card.get('question', '').strip()
                answer = card.get('answer', '').strip()
                module = card.get('module', 'Generated').strip()
                
                if question and answer:  # Only save if both question and answer exist
                    writer.writerow([question, answer, module, None])  # No image for generated cards
                    count += 1
        
        return jsonify({"success": True, "count": count}), 200
        
    except Exception as e:
        import traceback
        error_detail = f"Error saving flashcards: {str(e)}\n{traceback.format_exc()}"
        if DEBUG_MODE:
            print(f"SAVE ERROR: {error_detail}")
        return jsonify({"error": error_detail}), 500

if __name__ == '__main__':
    images_dir = os.path.join('static', 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        
    app.run(debug=True, host="0.0.0.0")
