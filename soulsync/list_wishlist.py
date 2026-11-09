import os
import requests

def get_soulsync_headers():
    api_key = os.environ.get("SOULSYNC_API_KEY")
    if not api_key:
        raise ValueError("Variabile d'ambiente SOULSYNC_API_KEY non impostata.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

def main():
    url = "https://soulsync.michelecapicchioni.com/api/v1/wishlist"
    try:
        headers = get_soulsync_headers()
        print("Richiesta wishlist in corso...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            res_data = response.json()
            tracks = res_data.get("data", {}).get("tracks", [])
            total_tracks = len(tracks)
            print(f"Brani in wishlist trovati: {total_tracks}\n")
            
            for idx, track in enumerate(tracks, 1):
                name = track.get("track_name", "Sconosciuto")
                artist = track.get("artist_name", "Sconosciuto")
                album = track.get("album_name", "N/D")
                spotify_id = track.get("spotify_track_id", "N/D")
                reason = track.get("failure_reason", "Nessun motivo specificato")
                
                print(f"[{idx}] {artist} - {name}")
                print(f"    Album: {album}")
                print(f"    ID Spotify: {spotify_id}")
                print(f"    Motivo Fallimento: {reason}")
                print("-" * 50)
        else:
            print(f"Errore {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Si è verificato un errore: {e}")

if __name__ == "__main__":
    main()
