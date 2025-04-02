import os
import sys
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

# Ensure Python can find modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import functions from solver and OCR
from solver import solve_problem
from ocr import extract_text_from_image
from utils.text_processing import clean_text

app = Flask(__name__)

# Upload folder setup
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

# Ensure uploads directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/solve", methods=["POST"])
def solve():
    question_text = ""
    image_provided = False
    
    # If text input is provided
    if "question_text" in request.form:
        question_text = request.form.get("question_text", "").strip()
    
    # If an image is uploaded
    if "question_image" in request.files:
        image = request.files["question_image"]
        if image.filename != "" and allowed_file(image.filename):
            image_provided = True
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)
            
            # Extract text from the image using OCR
            extracted_text = extract_text_from_image(image_path)
            if extracted_text:
                question_text = extracted_text

    # Validate input
    if not question_text:
        if image_provided:
            return jsonify({"error": "Could not extract text from the image. Please try again or enter the problem manually."})
        return jsonify({"error": "Please enter a math problem or upload an image."})

    # Clean the text (optional, depending on your needs)
    # question_text = clean_text(question_text)
    
    # Solve the problem
    problem_statement, solution_steps = solve_problem(question_text)
    
    return jsonify({
        "problem_statement": problem_statement,
        "solution_steps": solution_steps
    })

@app.route("/result", methods=["GET"])
def result():
    problem = request.args.get("problem", "")
    solution = request.args.get("solution", "")
    return render_template("result.html", 
                           problem_statement=problem, 
                           solution_steps=solution)

if __name__ == "__main__":
    app.run(debug=True)
