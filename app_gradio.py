import gradio as gr
import boto3
import os
import requests
import tempfile
from dotenv import load_dotenv

load_dotenv()

accessKeyId = os.environ.get('ACCESS_KEY_ID')
secretKey = os.environ.get('ACCESS_SECRET_KEY')
bucket_source = os.environ.get('BUCKET_SOURCE')
bucket_dest = os.environ.get('BUCKET_DEST')
region = os.environ.get('REGION')

# Cliente S3
s3_client = boto3.Session(
    aws_access_key_id=accessKeyId,
    aws_secret_access_key=secretKey,
    region_name=region).client('s3')

FLASK_API_URL = "http://127.0.0.1:5000/api/analyze"


def process_pipeline(image_filepath):
    if not image_filepath:
        return "Por favor, sube una imagen.", None

    # Extraemos el nombre del archivo
    filename = os.path.basename(image_filepath)

    try:
        # 1. Subir la imagen al bucket origen
        s3_client.upload_file(image_filepath, bucket_source, filename)

        # 2. Hacer la petición a nuestro servidor Flask
        response = requests.post(FLASK_API_URL, json={"key": filename})

        if response.status_code != 200:
            return f"Error en la API de Flask: {response.text}", None

        data = response.json()
        audio_key = data['audio_key']
        story_text = data['story_text']

        # 3. Descargar el MP3 a la carpeta temporal del sistema (NO al workspace)
        temp_dir = tempfile.gettempdir()
        local_audio_path = os.path.join(temp_dir, f"temp_{audio_key}")
        s3_client.download_file(bucket_dest, audio_key, local_audio_path)

        return story_text, local_audio_path

    except Exception as e:
        return f"Ocurrió un error en el flujo: {str(e)}", None


# --- Interfaz Gráfica (Dark Mode Negro/Rojo Nativo) ---
theme = gr.themes.Base(
    primary_hue="red",
    neutral_hue="slate",
    text_size=gr.themes.sizes.text_lg, # <-- AQUÍ AUMENTAMOS LA LETRA NATIVAMENTE
).set(
    body_background_fill="#000000",               # Fondo general negro puro
    block_background_fill="#0a0a0a",              # Fondo de las cajas casi negro
    block_border_width="1px",
    block_border_color="#991b1b",                 # Bordes en rojo oscuro
    block_label_text_color="#ff4d4d",             # Títulos (Ej: "Cuento Generado") en rojo neón
    table_text_color="#ffffff",                   # Texto interior en blanco puro
    button_primary_background_fill="#991b1b",     # Botón principal rojo oscuro
    button_primary_background_fill_hover="#ff4d4d", # Botón rojo vivo al pasar el ratón
    input_background_fill="#111111",              # Fondo interior del Textbox
)

# Definimos una altura estándar (en píxeles) para que ambos lados cuadren
IMAGE_HEIGHT = 500

with gr.Blocks(theme=theme, title="El Cuentacuentos Visual (AWS + AI)") as demo:
    gr.Markdown(
        """
        # El Cuentacuentos Visual
        
        Sube una imagen. Nuestro sistema detectará los elementos, creará un micro-cuento con IA y te lo leerá en voz alta.
        *(Arquitectura: AWS Rekognition -> S3 -> Gemini LLM -> AWS Polly)*
        """
    )

    with gr.Row(equal_height=True):
        # Columna Izquierda (Imagen y Botón)
        with gr.Column(scale=1):
            image_input = gr.Image(
                type="filepath",
                label="1. Sube tu imagen aquí",
                height=IMAGE_HEIGHT  # Forzamos la altura de la imagen
            )
            submit_btn = gr.Button("Analizar y Crear Cuento", variant="primary")

        # Columna Derecha (Texto y Audio)
        with gr.Column(scale=1):
            text_output = gr.Textbox(
                label="2. Cuento Generado (Gemini)",
                lines=13, # Ajustado a 13 para cuadrar con la imagen a 400px y la nueva letra grande
                max_lines=13,
                interactive=False
            )
            audio_output = gr.Audio(
                label="3. Reproductor (AWS Polly)",
                type="filepath"
            )

    submit_btn.click(
        fn=process_pipeline,
        inputs=image_input,
        outputs=[text_output, audio_output]
    )

if __name__ == "__main__":
    demo.launch()