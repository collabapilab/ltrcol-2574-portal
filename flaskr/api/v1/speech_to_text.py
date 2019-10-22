
import io
import os
import wave
import contextlib

from flask import jsonify, request
from flask import Blueprint

from flask_restplus import Namespace, Resource
from flaskr.utils import get_project_root

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types



api = Namespace('stt', description='Speech to text APIs')

project_root = get_project_root()
google_json = '/flaskr/data/json/google-speech.json'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(project_root) + google_json

@api.route("/<filename>/google_speech")
class google_speech_to_text_api(Resource):
    def get(self, filename):
        """
        Returns Google speech to text
        """

        project_root = get_project_root()

        # Instantiates a client
        client = speech.SpeechClient()

        # The name of the audio file to transcribe
        file_path = project_root / "flaskr" / "data" / "uploads" / filename

        with contextlib.closing(wave.open(str(file_path),'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            #print('duration', duration)
            
        # Loads the audio into memory
        with io.open(file_path, 'rb') as audio_file:
            content = audio_file.read()
            audio = types.RecognitionAudio(content=content)

        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=8000,
            language_code='en-US')

        # Detects speech in the audio file
        if duration < 60.0:
            response = client.recognize(config, audio)
        else:
            #print('long file')
            # todo: code for long files.  need to push to google storage first
            # https://cloud.google.com/speech-to-text/quotas
            response = client.long_running_recognize(config, audio)
        #print(response)

        transcripts = []
        for result in response.results:
            #print('Transcript: {}'.format(result.alternatives[0].transcript))
            transcripts.append(result.alternatives[0].transcript)

        return jsonify({'data': transcripts})

