import json
import requests
import urllib

from flask import current_app

from flaskr.db import get_db


API_URL_BASE = 'https://fortniteapi.io/'


def aggregate_global_data(data, key):
    aggr_result = 0
    for _, local_data in data.get('global_stats').items():
        aggr_result = aggr_result + local_data.get(key, 0)

    return aggr_result


def fetch_player_fortnite_data(gamer_tag):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': current_app.config['FORTNITE_TOKEN']
    }

    api_url = '%sstats?account=%s' % (API_URL_BASE, urllib.parse.quote(gamer_tag))
    return requests.get(api_url, headers=headers)


def get_account_id_from_username(username):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': current_app.config['FORTNITE_TOKEN']
    }

    api_url = '%slookup?username=%s' % (API_URL_BASE, urllib.parse.quote(username))
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        json_response = json.loads(response.content.decode('utf-8'))
        if json_response.get('result'):
            return json_response.get('account_id')


def sync_fortnite_user_with_tag(user_id, gamer_tag, db=None):
    """Fetch data for a user from fortnite and update its data.

    Return True if we succeed to fetch the data, False otherwise.
    """
    response = fetch_player_fortnite_data(gamer_tag)
    if response.status_code == 200:
        json_response = json.loads(response.content.decode('utf-8'))
        if db is None:
            db = get_db()
        top1 = aggregate_global_data(json_response, 'placetop1')
        kills = aggregate_global_data(json_response, 'kills')
        matches_played = aggregate_global_data(json_response, 'matchesplayed')

        db.execute(
            'REPLACE INTO fortnite_stats (user_id, top1, kills, matchesplayed) '
            'VALUES (?, ?, ?, ?)',
            (user_id, top1, kills, matches_played)
        )
        db.commit()
        return True
    return False
