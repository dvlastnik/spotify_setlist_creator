import argparse
import spotipy
import requests
import os
from dotenv import load_dotenv

load_dotenv()
SETLIST_FM_API_KEY = os.getenv("SETLIST_FM_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

def _get_artist_mbid(artist_name: str, headers: dict) -> str | None:
    """Fetches the unique MusicBrainz ID (MBID) for an exact artist match."""
    url = "https://api.setlist.fm/rest/1.0/search/artists"
    params = {
        "artistName": artist_name,
        "p": 1,
        "sort": "relevance"
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return None
        
    data = response.json()
    if 'artist' in data and data['artist']:
        for artist in data['artist']:
            if artist['name'].lower() == artist_name.lower():
                return artist['mbid']
    
    return None

def get_latest_setlist(artist_name: str) -> dict:
    """Searches for an artist by MBID and fetches their most recent populated setlist."""
    headers = {
        "x-api-key": SETLIST_FM_API_KEY,
        "Accept": "application/json"
    }
    
    print(f"Getting mbid for {artist_name}...")
    mbid = _get_artist_mbid(artist_name, headers)
    if not mbid:
        print(f"Could not find mbid for artist: {artist_name}")
        return None, None
        
    url = "https://api.setlist.fm/rest/1.0/search/setlists"
    params = {
        "artistMbid": mbid,
        "p": 1
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error fetching setlist: HTTP {response.status_code}")
        return {}

    data = response.json()
    if 'setlist' not in data or not data['setlist']:
        print(f"No setlists found for artist: {artist_name}")
        return {}

    for setlist in data['setlist']:
        songs = []
        if 'sets' in setlist and 'set' in setlist['sets']:
            for s in setlist['sets']['set']:
                for song in s.get('song', []):
                    if 'name' in song and song['name']:
                        songs.append(song['name'])
        
        if songs:
            actual_artist_name = setlist['artist']['name']
            event_date = setlist['eventDate']
            venue_def = setlist['venue']
            venue = venue_def['name']
            city = venue_def['city']['name']
            country = venue_def['city']['country']['name']
            
            print(f"Found latest populated setlist: {event_date} at {venue}")
            return {
                "artist_name": actual_artist_name,
                "songs": songs,
                "date": event_date,
                "venue": venue,
                "city": city,
                "country": country
            }

    print("Found recent gigs, but nobody has uploaded the songs for them yet!")
    return {}

def create_spotify_playlist(setlist_dict: dict) -> None:
    """Searches for tracks and creates or updates a Spotify playlist."""
    print("\nConnecting to Spotify...")

    artist = setlist_dict.get('artist_name', None)
    songs = setlist_dict.get('songs', [])
    date = setlist_dict.get('date', None)
    venue = setlist_dict.get('venue', None)
    city = setlist_dict.get('city', None)
    country = setlist_dict.get('country', None)
    
    scope = "playlist-modify-public playlist-read-private"
    sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=scope,
        show_dialog=True
    ))
    
    playlist_name = f"{artist} setlist"
    playlist_desc = f"Recent setlist from {artist}'s show at {venue} ({city}, {country}) on {date}. Taken from setlist.fm."

    print("Checking your library for existing playlists...")
    existing_playlist_id = None
    playlists = sp.current_user_playlists()
    while playlists:
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                existing_playlist_id = playlist['id']
                break
        
        if existing_playlist_id or not playlists['next']:
            break
        playlists = sp.next(playlists)

    if existing_playlist_id:
        print(f"Found existing playlist: '{playlist_name}'. Preparing to overwrite...")
        target_playlist_id = existing_playlist_id
        sp.user_playlist_change_details(user=sp.me(), playlist_id=target_playlist_id, description=playlist_desc)
    else:
        print(f"Creating new playlist: '{playlist_name}'")
        new_playlist = sp.current_user_playlist_create(
            name=playlist_name, 
            public=True, 
            description=playlist_desc
        )
        target_playlist_id = new_playlist['id']

    track_uris = []
    print("Searching for tracks on Spotify...")
    for song in songs:
        query = f"artist:{artist} track:{song}"
        result = sp.search(q=query, type='track', limit=1)
        
        items = result['tracks']['items']
        if items:
            track_uris.append(items[0]['uri'])
            print(f" [+] Found: {song}")
        else:
            fallback_query = f"track:{song}"
            fallback_result = sp.search(q=fallback_query, type='track', limit=1)
            
            fallback_items = fallback_result['tracks']['items']
            if fallback_items:
                track_uris.append(fallback_items[0]['uri'])
                found_artist = fallback_items[0]['artists'][0]['name']
                print(f" [~] Found (Fallback): {song} (Matched to: {found_artist})")
            else:
                print(f" [-] Missing: {song} (Could not find on Spotify at all)")

    if track_uris:
        sp.playlist_replace_items(playlist_id=target_playlist_id, items=track_uris[:100])
        for i in range(100, len(track_uris), 100):
            sp.playlist_add_items(playlist_id=target_playlist_id, items=track_uris[i:i+100])
            
        print(f"\nSuccess! Synced {len(track_uris)} tracks to your Spotify account.")
        print(f"Check your Spotify app, the playlist is ready!")
    else:
        print("\nNo tracks were found to add to the playlist.")

def parse_args():
    parser = argparse.ArgumentParser(description="Spotify setlist creator")
    parser.add_argument(
        "--artist",
        type=str,
        help="Artist name"
    )

    return parser.parse_args()

def main():
    args = parse_args()

    if args.artist is None:
        print("Artist name was not provided!")
        return

    setlist_dict = get_latest_setlist(args.artist)
    artist_name = setlist_dict.get('artist_name', None)
    if not artist_name:
        return

    # Dummy print
    print(f"Band: {artist_name}")
    print("Setlist:")
    for i, song in enumerate(setlist_dict['songs']):
        print(f"{i}. {song}")
    print()

    create_spotify_playlist(setlist_dict)

if __name__ == "__main__":
    main()
