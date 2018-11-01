from datetime import datetime

APIURL = 'https://kitsu.io/api/edge'
OAUTHURL = 'https://kitsu.io/api/oauth/token'
CLIENT_ID = 'dd031b32d2f56c990b1425efe6c42ad847e7fe3ab46bf1299f05ecd856bdb7dd'
CLIENT_SECRET = '54d7307928f63414defd96399fc31ba847961ceaecef3a5fd93144e960c0e151'

def authenticate():
    username = Prefs['kitsu_username']
    password = Prefs['kitsu_password']

    if username is None or password is None:
        Data.Remove('kitsu_token')
        Data.Remove('kitsu_refresh')
        Data.Remove('kitsu_token')
        Data.Remove('algolia_media')
        return

    token = Data.Load('kitsu_token')
    if token is None:
        return login(username, password)

    expires = datetime.fromtimestamp(float(Data.Load('kitsu_expires')))
    if datetime.now() > expires:
        return refresh(Data.Load('kitsu_refresh'))

    return token

def save_token(token):
    Data.Save('kitsu_expires',
              str(token['created_at'] + token['expires_in']))
    Data.Save('kitsu_token', token['access_token'])
    Data.Save('kitsu_refresh', token['refresh_token'])

def login(username, password):
    request = HTTP.Request(
        OAUTHURL,
        headers = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        },
        values = {
            'grant_type': 'password',
            'username': username,
            'password': password
        }
    )
    try:
        request.load()
        token = JSON.ObjectFromString(request.content)
        save_token(token)
        return token['access_token']
    except:
        Log.Error('Error logging in to Kitsu')

def refresh(refresh_token):
    request = HTTP.Request(
        OAUTHURL,
        headers = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        },
        values = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
    )
    try:
        request.load()
        token = JSON.ObjectFromString(request.content)
        save_token(token)
        return token['access_token']
    except:
        Log.Error('Error refreshing Kitsu token')
        username = Prefs['kitsu_username']
        password = Prefs['kitsu_password']
        return login(username, password)

def algolia_key():
    media_key = Data.Load('algolia_media')
    if media_key is not None:
        return media_key

    headers = {
        'Accept': 'application/vnd.api+json',
        'Content-Type': 'application/vnd.api+json'
    }

    token = authenticate()
    if token is None:
        anon_key = Data.Load('algolia_anon')
        if anon_key is not None:
            return anon_key

    headers['Authorization'] = 'Bearer ' + token
    request = HTTP.Request(
        APIURL + '/algolia-keys',
        headers = headers
    )
    try:
        request.load()
        media_key = JSON.ObjectFromString(request.content)['media']['key']
        if token is not None:
            Data.Save('algolia_media', media_key)
        else:
            Data.Save('algolia_anon', media_key)
        return media_key
    except:
        Log.Error('Error getting Algolia key')

def get_anime(id):
    headers = {
        'Accept': 'application/vnd.api+json',
        'Content-Type': 'application/vnd.api+json'
    }

    token = authenticate()
    if token is not None:
        headers['Authorization'] = 'Bearer ' + token

    request = HTTP.Request(
        'https://kitsu.io/api/edge/anime/' + id +
            '?include=categories,episodes,animeProductions.producer,' +
            'characters.character,characters.voices.person,staff.person,mappings',
        headers = headers
    )
    try:
        request.load()
        return JSON.ObjectFromString(request.content)
    except:
        Log.Error('Error getting anime info')
