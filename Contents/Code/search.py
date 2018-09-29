from kitsu import algolia_key

ALGOLIA_APP_ID = 'AWQO5J657S'

def search_anime(type, results, media, lang):
    query = media.show if type == 'tv' else media.name
    if media.year is not None:
        query += ' (' + media.year + ')'

    filters = '\\"kind:anime\\"'
    if type == 'movie':
        filters = filters + ',\\"subtype:movie\\"'

    request = HTTP.Request(
        'https://' + ALGOLIA_APP_ID + '-dsn.algolia.net/1/indexes/production_media/query',
        headers = {
            'Content-Type': 'application/json',
            'X-Algolia-Application-Id': ALGOLIA_APP_ID,
            'X-Algolia-API-Key': algolia_key()
        },
        data = '{"params":"query=' + query + '&facetFilters=[' + filters + ']"}'
    )
    try:
        request.load()
    except:
        Log.Error('Error searching Kitsu - Anime: ' + query)
        return
    result = JSON.ObjectFromString(request.content)

    s = 100
    for h in result['hits']:
        name = h['canonicalTitle']
        if type == 'tv':
            name = name + ' (' + h['subtype'] + ')'
        results.Append(MetadataSearchResult(
            id = str(h['id']),
            name = h['canonicalTitle'],
            year = h['year'],
            score = s,
            lang = lang
        ))
        s = s - 1
