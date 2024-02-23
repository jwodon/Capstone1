import requests
import os
import time
import json
from config import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET

client_id = TWITCH_CLIENT_ID
client_secret = TWITCH_CLIENT_SECRET
base_url = 'https://api.igdb.com/v4'


def get_twitch_access_token():
    resp = requests.post("https://id.twitch.tv/oauth2/token",
        params={"client_id": client_id, "client_secret": client_secret, "grant_type": 'client_credentials'})
    
    token = resp.json()['access_token']
    return token

def get_game_info(limit=20, offset=0):
    token = get_twitch_access_token()
    headers = {
        "Client-ID": client_id,  
        "Authorization": f"Bearer {token}" 
    }
    endpoint = "https://api.igdb.com/v4/games"
    data = f"fields name,summary,cover.url,genres.name,platforms.name,aggregated_rating,aggregated_rating_count,hypes; sort hypes desc; where hypes != 0; limit {limit}; offset {offset};"

    print("Data payload:", data)  # Print the data payload for debugging purposes

    response = requests.post(endpoint, headers=headers, data=data)  
    response_data = response.json()

    games_info = []
    for game in response_data:
            print("Game object:", game)  # Log the entire game object
            game_info = {
                "id": game.get("id"),
                "name": game.get("name"),
                "summary": game.get("summary"),
                "aggregated_rating": game.get("aggregated_rating"),
                "aggregated_rating_count": game.get("aggregated_rating_count"),           
                "cover_url": game.get("cover", {}).get("url"),
                "genres": [genre.get("name") for genre in game.get("genres", [])],
                "platforms": [platform.get("name") for platform in game.get("platforms", [])],
                "hypes": game.get("hypes")
            }
            games_info.append(game_info)

    return games_info


def get_platforms_info(limit=500):
    token = get_twitch_access_token()
    headers = {
        "Client-ID": client_id,  
        "Authorization": f"Bearer {token}" 
    }

    endpoint = "https://api.igdb.com/v4/platforms"
    fields = "name"  
    params = {
        "fields": fields,
        "limit": limit,
        "where": "category = (1,2,3,4,5,6)"
    }

    response = requests.post(endpoint, headers=headers, params=params)  

    return response

def get_genres_info(limit=500):
    token = get_twitch_access_token()
    headers = {
        "Client-ID": client_id,  
        "Authorization": f"Bearer {token}" 
    }

    endpoint = "https://api.igdb.com/v4/genres"
    fields = "name"  
    params = {
        "fields": fields,
        "limit": limit,
    }

    response = requests.post(endpoint, headers=headers, params=params)  

    return response

def get_single_game_info(game_id):
    token = get_twitch_access_token()
    headers = {
        "Client-ID": client_id,  
        "Authorization": f"Bearer {token}" 
    }

    endpoint = f"https://api.igdb.com/v4/games/{game_id}"
    fields = "name,summary,cover.url,genres.name,platforms.name, screenshots.url"  # Specify the fields you need
    params = {
        "fields": fields,
    }

    response = requests.get(endpoint, headers=headers, params=params)
    game_info = response.json()  

    # Ensure that game_info is a single dictionary, not a list
    if isinstance(game_info, list):
        return game_info[0]  # Assuming the first item is the desired game
    else:
        return game_info



