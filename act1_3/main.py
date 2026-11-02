import os
from dotenv import load_dotenv
from atproto import Client
from pymongo import MongoClient
import re
from google import genai

# Cargar variables de entorno
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Crear cliente de Gemini
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

if not GEMINI_API_KEY:
    raise ValueError("No se ha encontrado la API Key de Gemini")

print("API Key de Gemini cargada correctamente")

response = gemini_client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Responde únicamente: HOLA"
)

print(response.text)

IDENTIFICADOR_BSKY = os.getenv("IDENTIFICADOR_BSKY")
PASSWORD_BSKY = os.getenv("PASSWORD_BSKY")

if not IDENTIFICADOR_BSKY or not PASSWORD_BSKY:
    raise ValueError("No se han encontrado las credenciales de Bluesky")

print("Credenciales cargadas correctamente")

client = Client()
client.login(IDENTIFICADOR_BSKY, PASSWORD_BSKY)


def limpiar_texto(texto):
    """
    Elimina URLs y espacios innecesarios.
    """
    texto = re.sub(r'https?://\S+', '', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def obtener_feed(client, actor, limit=100):
    """
    Obtiene las publicaciones de un perfil de Bluesky.
    """

    feed = client.get_author_feed(actor, limit=limit)

    publicaciones = []

    for elemento in feed.feed:

        post = elemento.post

        # Obtener el texto de la publicación
        texto = getattr(post.record, "text", "")

        # Limpiar el texto
        texto_limpio = limpiar_texto(texto)

        # Ignorar publicaciones vacías
        if not texto_limpio:
            continue

        publicacion = {
            "uri": post.uri,
            "autor": actor,
            "texto_original": texto,
            "texto_limpio": texto_limpio
        }

        publicaciones.append(publicacion)

    return publicaciones


# actor = "sarahedo.bsky.social"

# publicaciones = obtener_feed(client, actor, limit=20)

# for publicacion in publicaciones:
#     print(publicacion["texto_limpio"])
#     print("-" * 50)

# print(f"Publicaciones obtenidas: {len(publicaciones)}")


def guardar_en_mongo(publicaciones, coleccion):
    """
    Guarda las publicaciones en MongoDB.
    Evita duplicados utilizando la URI de cada publicación.
    """

    for publicacion in publicaciones:
        coleccion.update_one(
            {"uri": publicacion["uri"]},
            {"$set": publicacion},
            upsert=True
        )

    print(f"Se han procesado {len(publicaciones)} publicaciones.")


# mongo_client = MongoClient(os.getenv("MONGODB_URI"))

# # Seleccionar base de datos y colección
# db = mongo_client["bluesky_db"]
# coleccion = db["publicaciones"]

# actor = "sarahedo.bsky.social"

# publicaciones = obtener_feed(client, actor, limit=10)

# guardar_en_mongo(publicaciones, coleccion)