# Spotify Setlist Creator
Python CLI tool for live music fans. This script automatically finds the most recent live concert setlist for any band using the [setlist.fm](https://www.setlist.fm/) API and generates (or updates) a Spotify playlist with those exact songs. 

## Prerequisites
You will need API access to both Setlist.fm and Spotify.

1. **Setlist.fm API Key:**
   - Create an account at [setlist.fm](https://www.setlist.fm/).
   - Go to your Settings > API to apply for a free API key.
2. **Spotify Developer Credentials:**
   - Log into the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
   - Click **Create App**. 
   - In the app settings, set your **Redirect URI** to `http://127.0.0.1:8888/callback`.
   - Open "User Management" in your app settings and add the email address linked to your personal Spotify account.
   - Save your **Client ID** and **Client Secret**.

## Installation

This project uses [uv](https://github.com/astral-sh/uv), better than classic pip, **BUT** if you really want to use pip, there is `requirements.txt`.

1. **Clone the repository:**
```bash
git clone https://github.com/dvlastnik/spotify_setlist_creator.git
cd spotify-setlist-creator
```

2. **Create a virtual environment and install dependencies:**
```bash
uv venv
uv pip install spotipy requests python-dotenv
```

3. **Configure your Environment Variables:**
Crate `.env` file in the root directory of the project and add API keys.
```bash
SETLIST_FM_API_KEY="your_setlist_fm_api_key_here"
SPOTIFY_CLIENT_ID="your_spotify_client_id_here"
SPOTIFY_CLIENT_SECRET="your_spotify_client_secret_here"
SPOTIFY_REDIRECT_URI="http://127.0.0.1:8888/callback"
```

## Usage
```bash
# Single word artist
uv run main.py --artist gojira

# Multi-word artist
uv run main.py --artist "iron maiden"
```

### IMPORTANT!
The very first time you run this script, your default web browser will open to a Spotify authorization page.

1. Log in with the Spotify account you added to your Developer Dashboard allowlist.
2. Click Agree to grant the app permission to manage your playlists.

### Example output
```
spotify_setlist_creator % uv run main.py --artist "iron maiden"
Getting mbid for iron maiden...
Found latest populated setlist: 02-08-2025 at PGE Narodowy
Band: Iron Maiden
Setlist:
0. Doctor Doctor
1. The Ides of March
2. Murders in the Rue Morgue
3. Wrathchild
4. Killers
5. Phantom of the Opera
6. The Number of the Beast
7. The Clairvoyant
8. Powerslave
9. 2 Minutes to Midnight
10. Rime of the Ancient Mariner
11. Run to the Hills
12. Seventh Son of a Seventh Son
13. The Trooper
14. Hallowed Be Thy Name
15. Iron Maiden
16. Churchill's Speech
17. Aces High
18. Fear of the Dark
19. Wasted Years
20. Always Look on the Bright Side of Life


Connecting to Spotify...
Checking your library for existing playlists...
Creating new playlist: 'Iron Maiden setlist'
Searching for tracks on Spotify...
 [+] Found: Doctor Doctor
 [+] Found: The Ides of March
 [+] Found: Murders in the Rue Morgue
 [+] Found: Wrathchild
 [+] Found: Killers
 [+] Found: Phantom of the Opera
 [+] Found: The Number of the Beast
 [+] Found: The Clairvoyant
 [+] Found: Powerslave
 [+] Found: 2 Minutes to Midnight
 [+] Found: Rime of the Ancient Mariner
 [+] Found: Run to the Hills
 [+] Found: Seventh Son of a Seventh Son
 [+] Found: The Trooper
 [+] Found: Hallowed Be Thy Name
 [~] Found (Fallback): Iron Maiden (Matched to: Iron Maiden)
 [+] Found: Churchill's Speech
 [+] Found: Aces High
 [+] Found: Fear of the Dark
 [+] Found: Wasted Years
 [~] Found (Fallback): Always Look on the Bright Side of Life (Matched to: Monty Python)

Success! Synced 21 tracks to your Spotify account.
Check your Spotify app, the playlist is ready!
```