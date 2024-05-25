from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import pandas as pd 
import matplotlib
matplotlib.use('module://matplotlib_inline.backend_inline')
import matplotlib.pyplot as plt

load_dotenv()



client_id= os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
#Funcion para obtener el toke de backend
def get_token():
    #Crear el string de autorizacion que codificamos con basae 64
    #Debemos tomar nuestr client id =, concatenarlo con el client secret y codificarlos usando base 64. Eso lo enviamos para llamar el token de autorizacion
    #Creando el string que concatema ambos clients
    auth_string = client_id + ":" + client_secret
    #codificando el string
    auth_bytes = auth_string.encode('utf-8')
    #Codificar utilizando base 64
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
#esto nos va a entregar un objeto tipo 64
    #Escribir el url al que enviaremos la peticion
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic "+ auth_base64, 
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No hay ningun artista con este nombre")
        return None
    return json_result[0]


def get_song_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    #print("Response Status Code:", result.status_code)
    #print("Response Content:", result.content)
    if result.status_code != 200:
        print("Failed to fetch top tracks:")
        return None
    
    json_result = json.loads(result.content)
    if 'tracks' not in json_result:
        print("No 'tracks' key in response:", json_result)
        return None
    
    return json_result['tracks']

token = get_token()
result = search_for_artist(token, "Mac Miller")
artist_id = result["id"] 
songs = get_song_by_artist(token, artist_id)


#for idx, song in enumerate(songs):
   # print(f'{idx + 1}. {song["name"]}')

track_ids = [track["id"] for track in songs]

#print(track_ids)

def get_track_details(token, track_ids):
    ids_string = ",".join(track_ids)
    url =f"https://api.spotify.com/v1/tracks?ids={ids_string}"
    headers = get_auth_header(token)
    result= get(url, headers=headers)
    if result.status_code != 200:
        print("No es posible encontrar los detalles", result. content)
        return None
    json_result = json.loads(result.content)
    return json_result['tracks']



token = get_token()
result = search_for_artist(token, "Mac Miller")
if result:
    artist_id = result["id"]
    songs = get_song_by_artist(token, artist_id)
    if songs:
        song_ids = [song['id'] for song in songs]
        songs_details = get_track_details(token, song_ids)
        if songs_details:
            df = pd.DataFrame(songs_details)
            df2 = df[['name', 'popularity', 'duration_ms']]
            df2.loc[:,'duration_ms'] = df2['duration_ms'] / 1000 / 60
            df2 = df2.rename(columns={"duration_ms": "Duracion", "name": "Nombre", "popularity":"Popularidad"})
            

print(df2.head(3))

#¿Tiene relación la duración con la popularidad? ¿Podríamos decir que una canción que dure poco tiempo puede ser más popular que otra que dure más? Analízalo graficando un scatter plot y argumenta tu respuesta.

x = df2.Duracion
y = df2.Popularidad

plt.scatter(x, y)
plt.xlabel('Duracion en minutos')
plt.ylabel('Popularidad')
plt.title('Scatter Plot de Duracion vs Popularidad')
plt.show()

'''
No logre hacer que el plot fuera visible :c
pero aqui dejo el link de google colab donde 
hice el scatter plot 
https://colab.research.google.com/drive/1U8UnNL58NqFrJq_QumWwTzoXY1mf5fui?usp=sharing
'''

'''
COMO CONCLUSIONES RESPECTO AL ANALISIS DE LA RELACION ENTRE ESTOS DATOS
EN EL SCATTER PLOT NO VEMOS NINGUNA TENDENCIA CLARA, POR LO QUE INICIALMENTE
SE DESACARTARIA UNA CORRELACION, SIN EMBARGO PARA SER MAS METICULOSOS 
SE HA CALCULADO LA CORRELACION DE PEARSON PARA VER SI EN LOS NUMEROS 
SE ENCONTRABA LA CORRELACION, SIN EMBARGO EL RESULTADO TAMBIEN FUE 
CERCANO A CERO Y POR TANTO NEGATIVO A UNA CORRELACION EN ESTE ARTISTA 
ESPECIFICO


'''
