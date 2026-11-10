from flask import Flask, request, abort, Response, jsonify
import boto3, os
from dotenv import load_dotenv
from detect_labels import get_image_labels
from generate_audio_story import create_story_and_audio

load_dotenv()

accessKeyId = os.environ.get('ACCESS_KEY_ID')
secretKey = os.environ.get('ACCESS_SECRET_KEY')
bucket_dest = os.environ.get('BUCKET_DEST')

application = Flask(__name__)

# Cliente S3 para guardar el resultado final
s3 = boto3.Session(
    aws_access_key_id=accessKeyId,
    aws_secret_access_key=secretKey).resource('s3')


@application.route('/api/analyze', methods=['POST'])
def analyzeImage():
    key = request.get_json().get('key')
    if not key:
        abort(400, description="Falta la clave 'key' en el JSON.")

    try:
        # 1. Llamamos a Rekognition para sacar los conceptos
        labels = get_image_labels(key)

        if not labels:
            return jsonify({"error": "No se detectaron objetos claros en la imagen."}), 400

        # 2. Generamos el cuento (Gemini) y el audio (Polly)
        audio_buffer, text_story = create_story_and_audio(labels)

        # 3. Guardamos el MP3 final en el bucket destino
        result_key = f"story_{key.split('.')[0]}.mp3"
        s3.Object(bucket_dest, result_key).put(Body=audio_buffer, ContentType='audio/mpeg')

        # Devolvemos el nombre del archivo de audio creado y el texto del cuento
        return jsonify({
            "message": "Proceso completado",
            "audio_key": result_key,
            "story_text": text_story
        }), 200

    except Exception as error:
        print(f"Error interno: {error}")
        abort(500)


if __name__ == "__main__":
    application.debug = True
    application.run()