import os
import boto3
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configurar Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-3.5-flash')

# Configurar AWS Polly
polly_client = boto3.Session(
    aws_access_key_id=os.environ.get('ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('ACCESS_SECRET_KEY'),
    region_name=os.environ.get('REGION')).client('polly')


def create_story_and_audio(labels):
    """Pide un cuento a Gemini basado en las etiquetas y genera el audio con Polly."""

    # 1. Generación del texto (LLM) - Prompt mejorado para formato Markdown
    prompt = (
        f"Escribe un cuento mágico de máximo 6 líneas en español para niños."
        f"Debe incluir estos elementos: {', '.join(labels)} (traducidos al español). "
        f"FORMATEA LA RESPUESTA ASÍ ESTRICTAMENTE:\n"
        f"Titulo: [Título inventado para el cuento]\n\n"
        f"[Texto del cuento con saltos de línea legibles]"
    )

    try:
        gemini_response = model.generate_content(prompt)
        story_text = gemini_response.text.strip()

        # Polly lee fatal los hashtags de Markdown (###), así que los quitamos solo para el audio
        clean_text_for_polly = story_text.replace("###", "").replace("*", "")

        print(f"Cuento generado:\n{story_text}")
    except Exception as e:
        raise Exception(f"Error generando el texto con Gemini: {e}")

    # 2. Generación del audio (AWS Polly)
    try:
        polly_response = polly_client.synthesize_speech(
            Text=clean_text_for_polly,  # Le pasamos el texto limpio sin Markdown
            OutputFormat='mp3',
            VoiceId='Lucia',
            Engine='standard'
        )

        if "AudioStream" in polly_response:
            audio_buffer = polly_response["AudioStream"].read()
            print("Audio generado con AWS Polly exitosamente.")
            return audio_buffer, story_text  # Devolvemos el story_text original con Markdown para la UI
        else:
            raise Exception("No se encontró el flujo de audio en la respuesta de Polly.")

    except Exception as e:
        raise Exception(f"Error generando audio con Polly: {e}")