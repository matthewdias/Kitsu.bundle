from datetime import datetime, timedelta

APIKEY='88A8042EC60E49F5'
APIURL='https://api.thetvdb.com'

def authenticate():
    token = Data.Load('tvdb_token')
    if token is not None:
        expires = datetime.utcfromtimestamp(float(Data.Load('tvdb_expires')))
        if datetime.utcnow() > expires:
            return refresh(token)
        else:
            return token
    else:
        token = login()
        Data.Save('tvdb_expires', (datetime.utcnow() + timedelta(hours=24)).strftime('%s'))
        Data.Save('tvdb_token', token)
        return token

def login():
    request = HTTP.Request(
        APIURL + '/login',
        headers = { 'Content-Type': 'application/json' },
        data = '{"apikey":"' + APIKEY + '"}'
    )
    request.load()
    result = JSON.ObjectFromString(request.content)
    return result['token']

def refresh(token):
    request = HTTP.Request(
        APIURL + '/refresh_token',
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }
    )
    request.load()
    result = JSON.ObjectFromString(request.content)
    return result['token']

def get_series_name(id):
    token = authenticate()
    request = HTTP.Request(
        APIURL + '/series/' + id,
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }
    )
    request.load()
    result = JSON.ObjectFromString(request.content)
    return result['data']['seriesName']
