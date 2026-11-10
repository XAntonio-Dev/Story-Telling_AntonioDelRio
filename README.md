# El Cuentacuentos Visual (AWS + IA)

Proyecto desarrollado para el módulo de **Programación de Inteligencia Artificial (PIA)**, correspondiente a la Unidad 5.

El Cuentacuentos Visual es una aplicación que permite subir una imagen a través de una interfaz gráfica, analizar su contenido mediante inteligencia artificial y generar automáticamente un pequeño cuento basado en los elementos detectados. Finalmente, el cuento se convierte en un archivo de audio narrado en español para que el usuario pueda escucharlo desde la propia aplicación.

## Arquitectura y tecnologías utilizadas

El proyecto está dividido en varios componentes, cada uno encargado de una parte del proceso:

- **Backend:** Flask, encargado de gestionar las peticiones y coordinar el funcionamiento de los distintos servicios.
- **Frontend:** Gradio, utilizado para crear la interfaz gráfica con la que interactúa el usuario.
- **Visión artificial:** AWS Rekognition (`detect_labels`), encargado de analizar las imágenes e identificar los elementos que aparecen en ellas.
- **Almacenamiento:** AWS S3, utilizando dos buckets: uno para almacenar las imágenes originales y otro para guardar los audios generados.
- **Generación de texto:** Google Gemini 3.5 Flash, utilizado para crear un pequeño cuento a partir de las etiquetas detectadas en la imagen.
- **Síntesis de voz:** Amazon Polly (`synthesize_speech`), encargado de convertir el cuento generado en un archivo de audio MP3 narrado en español.

## Instalación y configuración

Para ejecutar el proyecto en un equipo local, es necesario seguir los siguientes pasos.

### 1. Clonar el repositorio

Clona el repositorio desde GitHub y accede a la carpeta del proyecto:

```bash
git clone https://github.com/XAntonio-Dev/Story-Telling_AntonioDelRio.git
cd Story-Telling_AntonioDelRio
```

### 2. Crear y activar un entorno virtual

Se recomienda utilizar un entorno virtual para instalar las dependencias del proyecto sin afectar a otras instalaciones de Python.

```bash
python -m venv .venv
```

Para activar el entorno virtual, utiliza el comando correspondiente a tu sistema operativo:

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 3. Instalar las dependencias

Con el entorno virtual activado, instala las librerías necesarias mediante el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

El proyecto necesita determinadas credenciales y datos de configuración para poder comunicarse con los servicios de AWS y Google Gemini.

Para ello:

1. Busca el archivo `.env.example` incluido en el proyecto.
2. Crea una copia con el nombre `.env`.
3. Completa las variables de configuración con tus propios datos.

Será necesario configurar las credenciales de AWS (Access Key y Secret Key), la región de AWS, los nombres de los buckets de S3 y la API Key de Google Gemini.

**Importante:** El archivo `.env` está incluido en `.gitignore` para evitar que las credenciales personales se suban accidentalmente al repositorio. No se deben compartir ni publicar estas claves.

## Ejecución del sistema

La aplicación utiliza dos procesos independientes que deben estar funcionando al mismo tiempo: el servidor API de Flask y la interfaz gráfica de Gradio.

Para iniciar el proyecto, abre dos terminales diferentes desde la carpeta principal del repositorio.

### Terminal 1: Servidor API de Flask

Activa el entorno virtual y ejecuta el siguiente comando:

```bash
python application.py
```

Este proceso inicia el servidor Flask, que recibe las peticiones de la interfaz y coordina el análisis de la imagen, la generación del cuento y la creación del audio.

### Terminal 2: Interfaz gráfica de Gradio

En una segunda terminal, con el mismo entorno virtual activado, ejecuta:

```bash
python app_gradio.py
```

Este proceso inicia la interfaz gráfica desde la que el usuario puede seleccionar una imagen y visualizar el resultado del procesamiento.

### Acceso a la aplicación

Una vez iniciados los dos procesos, Gradio mostrará en la terminal una dirección local para acceder a la aplicación desde el navegador.

Por defecto, suele estar disponible en:

```text
http://127.0.0.1:7860
```

Al acceder, el usuario podrá subir una imagen y comenzar el proceso de análisis. Cuando termine, la aplicación mostrará el cuento generado y permitirá reproducir el audio narrado.

## Funcionamiento general

De forma resumida, el funcionamiento de la aplicación sigue estos pasos:

1. El usuario selecciona y sube una imagen desde la interfaz de Gradio.
2. La imagen se almacena en el bucket de origen de Amazon S3.
3. Gradio envía una petición HTTP POST a Flask con la clave de la imagen.
4. Flask solicita a AWS Rekognition que analice la imagen y obtenga las etiquetas de los elementos detectados.
5. Las etiquetas obtenidas se envían a Google Gemini para generar un pequeño cuento.
6. El texto generado se envía a Amazon Polly para convertirlo en un archivo de audio MP3.
7. Flask almacena el audio en el bucket de destino de S3 y devuelve a Gradio la información del cuento y la clave del archivo de audio.
8. Finalmente, Gradio descarga el audio, muestra el cuento y permite escucharlo desde la propia interfaz.

