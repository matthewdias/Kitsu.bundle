from datetime import datetime, timedelta
from time import mktime

APIKEY='88A8042EC60E49F5'
APIURL='https://api.thetvdb.com'

def authenticate():
    token = Data.Load('tvdb_token')
    if token is not None:
        expires = datetime.fromtimestamp(float(Data.Load('tvdb_expires')))
        if datetime.now() > expires:
            return refresh(token)
        else:
            return token
    else:
        token = login()
        if token is not None:
            Data.Save('tvdb_expires',
                      str(mktime((datetime.now() + timedelta(hours=24)).timetuple())))
            Data.Save('tvdb_token', token)
        return token

def login():
    request = HTTP.Request(
        APIURL + '/login',
        headers = { 'Content-Type': 'application/json' },
        data = '{"apikey":"' + APIKEY + '"}'
    )
    try:
        request.load()
        result = JSON.ObjectFromString(request.content)
        return result['token']
    except:
        Log.Error('Error logging in to TVDB')


def refresh(token):
    request = HTTP.Request(
        APIURL + '/refresh_token',
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }
    )
    try:
        request.load()
        result = JSON.ObjectFromString(request.content)
        return result['token']
    except:
        Log.Error('Error refreshing TVDB token')


def get_series_name(id):
    token = authenticate()
    if token is None:
        return

    request = HTTP.Request(
        APIURL + '/series/' + id,
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }
    )
    try:
        request.load()
        result = JSON.ObjectFromString(request.content)
        return result['data']['seriesName']
    except:
        Log.Error('Error getting series name from TVDB')
