ALGOLIA_APP_ID = 'AWQO5J657S'
ALGOLIA_API_KEY = 'NzYxODA5NmY0ODRjYTRmMzQ2YjMzNzNmZmFhNjY5ZGRmYjZlMzViN2VkZDIzMGUwYjM5ZjQ5NjAwZGI4ZTc5MHJlc3RyaWN0SW5kaWNlcz1wcm9kdWN0aW9uX21lZGlhJmZpbHRlcnM9Tk9UK2FnZVJhdGluZyUzQVIxOA'

def search_anime(type, results, media, lang):
    query = media.show if type == 'tv' else media.name
    if media.year is not None:
        query += ' (' + media.year + ')'

    filters = '\\"kind:anime\\"'
    if type == 'movie':
        filters = filters = ',\\"subtype:movie\\"'

    request = HTTP.Request(
        'https://' + ALGOLIA_APP_ID + '-dsn.algolia.net/1/indexes/production_media/query',
        headers = {
            'Content-Type': 'application/json',
            'X-Algolia-Application-Id': ALGOLIA_APP_ID,
            'X-Algolia-API-Key': ALGOLIA_API_KEY
        },
        data = '{"params":"query=' + query + '&facetFilters=[' + filters + ']"}'
    )
    request.load()
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
