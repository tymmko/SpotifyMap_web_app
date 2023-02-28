"""a module for creting map for market availability for given artist"""
import base64
import json
from flask import Flask, render_template, request
import folium
from geopy.geocoders import Nominatim
import pycountry
from requests import post, get

CLIENT_ID = '910b4b3c014e48bfac5b92876a967470'
CLIENT_SECRET = 'b5dbc928ecb644e4b8b3ade2f44e3a63'
app = Flask(__name__)
@app.route('/search', methods=['POST'])
def get_id():
    """
    A module for calling for a map with given name.
    """
    name_art = request.form['artist_name']
    get_token(name_art)
    return render_template('Map.html')

@app.route('/')
@app.route('/entry')
def entry_page():
    """
    A module for requesting the name of the artist in main.html
    """
    return render_template('main.html')

def create_map(countries):
    """
    A module for creating a map with countries from available_market.
    """
    map_1 = folium.Map()
    dict_lat_long = {}
    geolocator = Nominatim(user_agent="my")
    for country in countries[:50]:
        try:
            country_1 = pycountry.countries.get(alpha_2=country)
            location = geolocator.geocode(country_1.name)
            latitude = location.latitude
            longitude = location.longitude
            dict_lat_long[country_1.name] = f'{latitude, longitude}'
        except AttributeError:
            continue
    for i in dict_lat_long.keys():
        latitude_1 = float(dict_lat_long[i].split(',')[0][1:])
        longitude_1 = float(dict_lat_long[i].split(',')[1][:-1])
        folium.Marker([latitude_1, longitude_1], popup=i).add_to(map_1)
    map_1.save('mysite/templates/Map.html')

def get_top_song(artist_name, auth_key):
    """
    A module for getting info about top song of the author.
    """
    search_header = {"Authorization": "Bearer " + auth_key}
    search_url = "https://api.spotify.com/v1/search?q=" + artist_name + "&type=artist"
    response = get(search_url, headers=search_header)
    artist_id = json.loads(response.text)["artists"]["items"][0]["id"]
    top_tracks_url = "https://api.spotify.com/v1/artists/" + artist_id + "/top-tracks?country=US"
    response = get(top_tracks_url, headers=search_header)
    top_track_id = json.loads(response.text)["tracks"][0]["id"]
    track_url = "https://api.spotify.com/v1/tracks/" + top_track_id
    response = get(track_url, headers=search_header)
    track_data = json.loads(response.text)
    track_markets = track_data["available_markets"]
    return track_markets

def get_token(name):
    """
    A module for getting.
    """
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic '+ auth_base64,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    result = post(url, headers = headers, data = data)
    json_result = json.loads(result.content)
    token = json_result['access_token']
    create_map(get_top_song(name, token))

if __name__ == '__main__':
    app.run(debug = True)
