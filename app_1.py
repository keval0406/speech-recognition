import soundfile as sf
import speech_recognition as sr
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import io
import base64
from uuid import uuid4
from pydub import AudioSegment
from string_preprocessing import process_recognition_results
import json

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Create the 'audios' directory if it doesn't exist
if not os.path.exists('audios'):
    os.makedirs('audios')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/speech_to_text', methods=['POST'])
def upload_audio():
    data = request.get_json()
    print(data.keys())
    # Check if audio data is in the request
    if 'audio' not in data:
        return jsonify({"error": "No audio data in the request"}), 400

    audio_data = data['audio']
    identifier = data['identifier']
    print(identifier)
    # Decode the audio data
    try:
        header, encoded = audio_data.split(',', 1)
        audio_bytes = base64.b64decode(encoded)
    except Exception as e:
        return jsonify({"error": "Invalid audio data format"}), 400

    fname = uuid4()
    fname = str(fname)[:4]
    # Save the audio file with a unique name using soundfile
    audio_path = os.path.join('audios', f"{fname}.wav")
    mp3_path = os.path.join('audios', f"{fname}.mp3")  # Path for the MP3 file
    try:
        # Convert byte data to numpy array and save using soundfile
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        sf.write(audio_path, audio_segment.get_array_of_samples(),
                 audio_segment.frame_rate)

        # Convert WAV to MP3
        audio_segment.export(mp3_path, format='mp3')  # Export as MP3
    except Exception as e:
        return jsonify({"error": f"Could not save audio file: {str(e)}"}), 500

    try:
        r = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)  # read the entire audio file

        try:
            text = r.recognize_google(audio)
            text = process_recognition_results(
                text, id=identifier)
            os.remove(mp3_path)
            os.remove(audio_path)
            return jsonify({"message": "File uploaded successfully", "transcription": text}), 200
        except sr.UnknownValueError:
            os.remove(mp3_path)
            os.remove(audio_path)
            return jsonify({"error": "Google Speech Recognition could not understand audio"}), 400
        except sr.RequestError as e:
            os.remove(mp3_path)
            os.remove(audio_path)
            return jsonify({"error": f"Could not request results from Google Speech Recognition service; {e}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 404
    



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
