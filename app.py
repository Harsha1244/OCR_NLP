from flask import Flask, render_template, request, redirect, url_for, flash
import os
import easyocr
import translators as ts
import webbrowser
from threading import Timer

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize the EasyOCR reader for Sanskrit (using Hindi model for similarity)
reader = easyocr.Reader(['en', 'hi'])

# Process the uploaded image
def process_image(image_path):
    # Read text from image
    output = reader.readtext(image_path, paragraph=True, batch_size=3)
    sans_text = "\n".join([item[1] for item in output])

    # Translate text to English
    translated_text = ts.google(query_text=sans_text, to_language='en')

    # Save translated text to file
    textfilename = os.path.splitext(os.path.basename(image_path))[0].lower()
    with open(f'results/{textfilename}.txt', 'w', encoding="utf-8") as f:
        f.write(f"Sanskrit Text:\n{sans_text}\n\nTranslated Text:\n{translated_text}")

    return sans_text, translated_text

# Route for the main page
@app.route("/")
def index():
    return render_template("index.html")

# Route for handling the upload
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file")
        return redirect(request.url)

    if file and file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        filepath = os.path.join("uploads", file.filename)
        file.save(filepath)
        sans_text, translated_text = process_image(filepath)
        return render_template("result.html", filename=file.filename, sans_text=sans_text, translated_text=translated_text)

    flash("Invalid file format. Only JPG and PNG are supported.")
    return redirect(url_for("index"))

# Open the browser after starting the Flask server
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    Timer(1, open_browser).start()  # Delay by 1 second before opening the browser
    app.run(debug=True)
