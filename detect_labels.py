import os
import boto3
from dotenv import load_dotenv

load_dotenv()

# Obtenemos las variables de entorno
accessKeyId = os.environ.get('ACCESS_KEY_ID')
secretKey = os.environ.get('ACCESS_SECRET_KEY')
bucket = os.environ.get('BUCKET_SOURCE')
region = os.environ.get('REGION')

# Inicializamos el cliente de Rekognition
rekognition_client = boto3.Session(
    aws_access_key_id=accessKeyId,
    aws_secret_access_key=secretKey,
    region_name=region).client('rekognition')

def get_image_labels(img_key):
    """Llama a AWS Rekognition y devuelve una lista de etiquetas en inglés."""
    try:
        response = rekognition_client.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': img_key}},
            MaxLabels=7,
            MinConfidence=80
        )
        # Extraemos solo el nombre de las etiquetas
        labels = [label['Name'] for label in response['Labels']]
        print(f"Etiquetas detectadas con éxito: {labels}")
        return labels
    except Exception as e:
        raise Exception(f"Error analizando la imagen en Rekognition: {e}")