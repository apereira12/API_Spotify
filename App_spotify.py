import os

import dotenv
import requests
import streamlit as st
from requests.auth import HTTPBasicAuth
from itertools import zip_longest

dotenv.load_dotenv(dotenv.find_dotenv())


def autenticar():
    #Autentica no Spotify e retorna o token de acesso
    # O token de acesso é necessário para fazer requisições à API do Spotify
    url = "https://accounts.spotify.com/api/token"
    body = {
        'grant_type': 'client_credentials',
    }
    usuario = os.environ['SPOTIFY_CLIENT_ID']
    senha = os.environ['SPOTIFY_CLIENT_SECRET']
    auth = HTTPBasicAuth(username=usuario, password=senha)

    resposta = requests.post(url=url, data=body, auth=auth)
    # O token de acesso é retornado no formato JSON
    # Se a requisição falhar, o token será None
    try:
        resposta.raise_for_status()
    except requests.HTTPError as e:
        print(f"Erro no request: {e}")
        token = None
    else:
        token = resposta.json()['access_token']
        print('Token obtido com sucesso!')
    return token


def busca_artista(nome_artista, headers):
    # Busca o artista na API do Spotify
    # Retorna o primeiro resultado da busca
    # Se não houver resultados, retorna None
    url = "https://api.spotify.com/v1/search"
    params = {
        'q': nome_artista,
        'type': 'artist',
    }
    resposta = requests.get(url=url, headers=headers, params=params)
    try:
        # Se a busca não retornar resultados, o primeiro resultado será None
        primeiro_resultado = resposta.json()['artists']['items'][0]
    except IndexError:
        primeiro_resultado = None
    return primeiro_resultado


def busca_top_musicas(id_artista, headers):
    url = f"https://api.spotify.com/v1/artists/{id_artista}/top-tracks"
    resposta = requests.get(url=url, headers=headers)
    musicas = resposta.json()['tracks']
    return musicas


def main():
    # Cabeçalho do Web App
    st.title('Consumo de API Spotify 🎵')
    st.write('fonte: https://developer.spotify.com/documentation/web-api')
    nome_artista = st.text_input('Informe o artista:')
    if not nome_artista:
        st.stop()

    # Autentica no Spotify
    token = autenticar()
    if not token:
        st.stop()
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Busca pelo artista
    artista = busca_artista(nome_artista=nome_artista, headers=headers)
    if not artista:  # Artista não encontrado
        st.warning(f'Sem dados para o artista {nome_artista}!')
        st.stop()

    # Extrai dados do artista
    id_artista = artista['id']
    nome_artista = artista['name']  # Atualiza para nome "oficial"
    popularidade_artista = artista['popularity']

    # Busca pelas top músicas do artista
    musicas = busca_top_musicas(id_artista=id_artista, headers=headers)

    # Exibe dados no Web App
    st.subheader(f'Artista: {nome_artista} (pop: {popularidade_artista})')
    st.write('Melhores músicas:')
    
    musicas_em_pares = zip_longest(musicas[::2], musicas[1::2])

    for musica1, musica2 in musicas_em_pares:
        with st.container(border=True):
            col1, col2 = st.columns(2)  # Cria duas colunas para exibir as músicas lado a lado
            
            # Primeira música
            if musica1:
                with col1:
                    nome_musica1 = musica1['name']
                    popularidade_musica1 = musica1['popularity']
                    link_musica1 = musica1['external_urls']['spotify']
                    link_em_markdown1 = f'[{nome_musica1}]({link_musica1})'
                    st.markdown(f'{link_em_markdown1}: (pop: {popularidade_musica1})')
                    st.image(musica1['album']['images'][0]['url'], width=200)
            
            # Segunda música
            if musica2:
                with col2:
                    nome_musica2 = musica2['name']
                    popularidade_musica2 = musica2['popularity']
                    link_musica2 = musica2['external_urls']['spotify']
                    link_em_markdown2 = f'[{nome_musica2}]({link_musica2})'
                    st.markdown(f'{link_em_markdown2}: (pop: {popularidade_musica2})')
                    st.image(musica2['album']['images'][0]['url'], width=200)
                


if __name__ == '__main__':
    main()
