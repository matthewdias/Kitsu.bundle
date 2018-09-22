from datetime import datetime
from thetvdb import get_series_name

VOICE_LANGUAGES = {
    'de': 'German',
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'he': 'Hebrew',
    'hu': 'Hungarian',
    'it': 'Italian',
    'ja_jp': 'Japanese',
    'ko': 'Korean',
    'pt_br': 'Portuguese',
}

def update_anime(type, metadata, media, force):
    request = HTTP.Request(
        'https://kitsu.io/api/edge/anime/' + metadata.id +
            '?include=categories,episodes,animeProductions.producer,' +
            'characters.character,characters.voices.person,staff.person,mappings',
        headers = {
            'Accept': 'application/vnd.api+json',
            'Content-Type': 'application/vnd.api+json'
        }
    )
    request.load()
    result = JSON.ObjectFromString(request.content)
    anime = result['data']['attributes']

    includes = {
        'categories': [],
        'episodes': [],
        'animeProductions': [],
        'producers': [],
        'mediaCharacters': [],
        'characters': [],
        'characterVoices': [],
        'people': [],
        'mediaStaff': [],
        'mappings': []
    }
    for include in result['included']:
        includes[include['type']].append(include)

    if metadata.genres is None or force:
        metadata.genres = map(lambda c: c['attributes']['title'], includes['categories'])

    if (metadata.duration is None or force) and anime['episodeLength'] is not None:
        metadata.duration = anime['episodeLength'] * 60000

    if (metadata.rating is None or force) and anime['averageRating'] is not None:
        metadata.rating = float(anime['averageRating']) / 10

    if (metadata.title is None or force) and anime['canonicalTitle'] is not None:
        metadata.title = anime['canonicalTitle']

    if (metadata.summary is None or force) and anime['synopsis'] is not None:
        metadata.summary = anime['synopsis']

    if (metadata.originally_available_at is None or force) and anime['startDate'] is not None:
        start_date = datetime.strptime(anime['startDate'], '%Y-%m-%d')
        metadata.originally_available_at = start_date

    if (metadata.content_rating is None or force) and anime['ageRatingGuide'] is not None:
        metadata.content_rating = anime['ageRatingGuide']

    if metadata.studio is None or force:
        anime_studio = find_first(lambda ap: ap['attributes']['role'] == 'studio',
            includes['animeProductions'])
        if anime_studio is not None:
            studio_id = anime_studio['relationships']['producer']['data']['id']
            studio = find_first(lambda p: p['id'] == studio_id, includes['producers'])
            if studio is not None:
                metadata.studio = studio['attributes']['name']

    if metadata.roles is None or force:
        for char in includes['mediaCharacters']:
            char_id = char['relationships']['character']['data']['id']
            character = find_first(lambda c: c['id'] == char_id, includes['characters'])
            if character is not None:
                voice_ids = map(lambda cv: cv['id'], char['relationships']['voices']['data'])
                voices = filter(lambda v: v['id'] in voice_ids, includes['characterVoices'])
                if voices is not None:
                    for voice in voices:
                        person_id = voice['relationships']['person']['data']['id']
                        person = find_first(lambda p: p['id'] == person_id, includes['people'])
                        if person is not None:
                            role = metadata.roles.new()
                            role.name = person['attributes']['name']
                            if person['attributes']['image'] is not None:
                                role.photo = person['attributes']['image']['original']

                            if voice['attributes']['locale'] is not None:
                                locale = voice['attributes']['locale']
                                locale = VOICE_LANGUAGES.get(locale, locale)
                                role.role = '{} ({})'.format(
                                    character['attributes']['canonicalName'], locale
                                )
                            else:
                                role.role = character['attributes']['canonicalName']

        for staff in includes['mediaStaff']:
            person_id = staff['relationships']['person']['data']['id']
            person = find_first(lambda p: p['id'] == person_id, includes['people'])
            if person is not None:
                role = metadata.roles.new()
                role.name = person['attributes']['name']
                if person['attributes']['image'] is not None:
                    role.photo = person['attributes']['image']['original']
                if staff['attributes']['role'] is not None:
                    role.role = staff['attributes']['role']

    if (metadata.posters is None or force) and anime['posterImage'] is not None:
        poster_image = anime['posterImage']
        thumbnail = Proxy.Preview(HTTP.Request(
            poster_image['tiny'], immediate = True
        ).content)
        metadata.posters[poster_image['large']] = thumbnail

    if type == 'tv':
        if (metadata.banners is None or force) and anime['coverImage'] is not None:
            cover_image = anime['coverImage']
            thumbnail = Proxy.Preview(HTTP.Request(
                cover_image['original'],
                immediate = True
            ).content)
            metadata.banners[cover_image['original']] = thumbnail

        update_episodes(media, metadata, force, includes['episodes'])

        if metadata.collections is None or force:
            update_collections(media, metadata, includes['mappings'])

    if type == 'movie':
        if (metadata.year is None or force) and anime['startDate'] is not None:
            metadata.year = int(anime['startDate'][:4])

def update_episodes(media, metadata, force, inc_episodes):
    for number in media.seasons[1].episodes:
        number = int(number)
        episode = metadata.seasons[1].episodes[number]

        ep = find_first(lambda e: e['attributes']['relativeNumber'] == number,
            inc_episodes)

        if ep is not None:
            ep = ep['attributes']

            if (episode.title is None or force) and ep['canonicalTitle'] is not None:
                episode.title = ep['canonicalTitle']

            if (episode.summary is None or force) and ep['synopsis'] is not None:
                episode.summary = ep['synopsis']

            if (episode.originally_available_at is None or force) and ep['airdate'] is not None:
                air_date = datetime.strptime(ep['airdate'], '%Y-%m-%d')
                episode.originally_available_at = air_date

            if (episode.thumbs is None or force) and ep['thumbnail'] is not None:
                thumb_image = ep['thumbnail']['original']
                thumbnail = Proxy.Preview(HTTP.Request(thumb_image, immediate = True).content)
                episode.thumbs[thumb_image] = thumbnail

            if (episode.duration is None or force) and ep['length'] is not None:
                episode.duration = ep['length'] * 60000

def update_collections(media, metadata, maps):
    tvdb = None
    mapping = find_first(lambda m: m['attributes']['externalSite'] == 'thetvdb', maps)
    if mapping is not None:
        tvdb = mapping['attributes']['externalId'].split('/')[0]
    else:
        mapping = find_first(lambda m: m['attributes']['externalSite'] == 'thetvdb/series', maps)
        if mapping is not None:
            tvdb = mapping['attributes']['externalId']
    if tvdb is not None:
        series_name = get_series_name(tvdb)
        metadata.collections = [series_name]

def find_first(p, list):
    for i in list:
        if p(i):
            return i
    return None
