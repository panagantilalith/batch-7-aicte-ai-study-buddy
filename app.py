 import re
from flask import Flask, render_template, request, redirect, url_for, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader

load_dotenv()

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ Use stable working model
# model = genai.GenerativeModel("gemini-1.5-pro-latest")
model = genai.GenerativeModel("models/gemini-flash-latest")
# Store generated outputs
generated_data = {
    "simple": "",
    "summary": "",
    "quiz": "",
    "ready": False
}


@app.route("/", methods=["GET", "POST"])
def index():
    global generated_data
    if request.method == "POST":
        text_input = request.form.get("text", "")
        file = request.files.get("file")
        extracted_text = ""

        # Extract PDF text if uploaded
        if file and file.filename.endswith(".pdf"):
            reader = PdfReader(file)
            for page in reader.pages:
                extracted_text += page.extract_text() or ""

        full_text = text_input + " " + extracted_text

        # 🔹 SIMPLE TERMS (clean + remove **)
        simple_raw = model.generate_content(
            f"""
            Explain the topic in very simple easy bullet points (5-8 points max).
            Use short sentences for students:
            {full_text}
            """
        ).text

        generated_data["simple"] = re.sub(r"\*\*", "", simple_raw)

        # 🔹 SUMMARY NOTES (headings format + remove **)
        summary_raw = model.generate_content(
            f"""
             Create a well structured study summary.

    Requirements:
    - Use clear side headings in plain plain text (NO **, NO markdown, NO symbols)
    - Each heading must end with a colon :
    - Headings should be short, meaningful, and visually strong titles
    - Under each heading, give 2-3 short explanation points
    - Use simple easy student-friendly language
    - Do NOT use stars (**), hashtags (#), bold, or numbering

    Strict Format:
    Important Topic Title:
      - explanation point 1
      - explanation point 2

    The headings should be clean titles so they can be displayed in large colored style in the UI.

    Generate the summary for:
            {full_text}
            """
        ).text

        generated_data["summary"] = re.sub(r"\*\*", "", summary_raw)

        # 🔹 QUIZ MCQ FORMAT
        quiz_raw = model.generate_content(
            f"""
            Create 5 MCQ questions from the text.

            Strict Format:
            Q1: question
            A) option
            B) option
            C) option
            D) option
            Answer: B

            Repeat same format for all questions.
            {full_text}
            """
        ).text

        generated_data["quiz"] = quiz_raw
        generated_data["ready"] = True

        return redirect(url_for("simple"))

    return render_template("index.html", ready=generated_data["ready"])


@app.route("/simple")
def simple():
    return render_template(
        "simple.html",
        data=generated_data["simple"],
        ready=generated_data["ready"]
    )


@app.route("/summary")
def summary():
    return render_template(
        "summary.html",
        data=generated_data["summary"],
        ready=generated_data["ready"]
    )


@app.route("/quiz")
def quiz():
    return render_template(
        "quiz.html",
        data=generated_data["quiz"],
        ready=generated_data["ready"]
    )


@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json["message"]
    result = model.generate_content(f"Answer clearly: {msg}")
    return jsonify({"reply": result.text})


if __name__ == "__main__":
    app.run(debug=True)