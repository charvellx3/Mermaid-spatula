
from flask import Flask, render_template, request, jsonify
from docx import Document
import boto3
import os
import uuid

app = Flask(__name__)
AUDIO_FOLDER = "static/audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Configure AWS Polly
polly_client = boto3.client('polly')

@app.route("/")
def index():
    voices = polly_client.describe_voices(LanguageCode='en-US')['Voices']
    return render_template("index.html", voices=voices)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["document"]
    voice_id = request.form["voice"]
    
    if file.filename.endswith(".docx"):
        document = Document(file)
        text = "\n".join([para.text for para in document.paragraphs])
        audio_filename = f"{uuid.uuid4().hex}.mp3"

        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId=voice_id
        )

        audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
        with open(audio_path, "wb") as f:
            f.write(response["AudioStream"].read())

        return {
            "success": True,
            "text": text,
            "audio_path": f"/static/audio/{audio_filename}"
        }
    
    return {"success": False, "error": "Only .docx files allowed"}

if __name__ == "__main__":
    app.run(debug=True)
