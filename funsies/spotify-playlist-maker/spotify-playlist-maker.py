import argparse
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def main():
    parser = argparse.ArgumentParser(description="Cria uma playlist no Spotify a partir de um CSV.")
    parser.add_argument("--playlist", required=True, help="Nome da playlist a ser criada")
    parser.add_argument("--file", required=True, help="Caminho do arquivo CSV com colunas: nome, banda")
    args = parser.parse_args()

    # CONFIGURAÇÕES DO SPOTIFY (coloque suas credenciais)
    CLIENT_ID = "ac83814154364b409a24b42fecae1a05"
    CLIENT_SECRET = "40e0045e902d4ba1b9b9f66d3ca900e0"
    REDIRECT_URI = "http://127.0.0.1:8000/callback"
    SCOPE = "playlist-modify-private playlist-modify-public"

    # AUTENTICAÇÃO
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        open_browser=True
    ))

    # LÊ O CSV
    df = pd.read_csv(args.file)

    if not all(col in df.columns for col in ["nome", "banda"]):
        raise ValueError("O CSV precisa ter colunas chamadas 'nome' e 'banda'.")

    # CRIA PLAYLIST NOVA
    user_id = sp.me()["id"]
    playlist = sp.user_playlist_create(user=user_id, name=args.playlist, public=False)
    playlist_id = playlist["id"]

    print(f"🎵 Criando playlist: {args.playlist}")

    tracks = []
    for _, row in df.iterrows():
        query = f"{row['nome']} {row['banda']}"
        result = sp.search(q=query, type="track", limit=1)
        items = result["tracks"]["items"]
        if items:
            track_uri = items[0]["uri"]
            tracks.append(track_uri)
            print(f"✔ Adicionado: {row['nome']} - {row['banda']}")
        else:
            print(f"❌ Não achei: {row['nome']} - {row['banda']}")

    # ADICIONA NA PLAYLIST EM BLOCOS (Spotify limita 100 por vez)
    for i in range(0, len(tracks), 100):
        sp.playlist_add_items(playlist_id, tracks[i:i+100])

    print(f"\n✅ Playlist '{args.playlist}' criada com {len(tracks)} músicas!")

if __name__ == "__main__":
    main()
