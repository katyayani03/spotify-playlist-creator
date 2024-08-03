from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "your_own_client_id"
CLIENT_SECRET = "your_own_client_secret"
REDIRECT_URI = "http://example.com"
USERNAME = "your_own_username"
example = "https://example.com/?code=AQC9sQRtGrwS4dvUpjRM4S25dnlK7INq1sw0zEJsTgyr21OuAbREh-jWz8RgTMkTNehxayMGCNluqyviVFhKZu9BgKeFiFnGkBEMhycsaIsOvrSQLhHJBHGPtcgjgqF6_mQNT-V9jaUu85Vj3ut7if2XFCVRXjM4exaOJ9ehkMpGynhyYsmN5wVQhWCwiL"

#obtaining authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope="playlist-modify-private",
                                               username=USERNAME,
                                               cache_path="token.txt"
                                               )
                     )

user_id = sp.current_user()["id"]

date = (input("Which year do you want to travel to? (YYYY-MM-DD): "))
BB_URL = f"https://www.billboard.com/charts/hot-100/{date}"
response = requests.get(url=BB_URL)
webpage = response.text

#using beautiful soup to scrape the billboard top 100 website and creating a list of songs and their artists
soup = BeautifulSoup(webpage, "html.parser")
songs = soup.select(selector="li h3", id="title-of-a-story")
artists = soup.select(selector="li ul li span", class_="c-label")[::7]
song_titles = [song.getText().strip() for song in songs][:100]
artist_names = [artist.getText().strip() for artist in artists][:100]

#search for songs in list from billboard in spotify and append it to a list
song_uris = []
for i in range(len(song_titles)):
    result = sp.search(q=f"track:{song_titles[i]} artist:{artist_names[i]}",
                       type="track",
                       limit=5
                       )

    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song_titles[i]} doesn't exist in Spotify. Skipped.")

#create a playlist in spotify
playlist_name = f"Billboard Top 100 {date}"
playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
playlist_id = playlist["id"]

#add the songs in our list to the playlist
sp.playlist_add_items(playlist_id, song_uris)
