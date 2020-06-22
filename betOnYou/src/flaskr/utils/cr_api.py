import json
import requests
import urllib

import click
from flask import current_app
from flask.cli import with_appcontext

from flaskr.db import get_db


API_URL_BASE = 'https://api.clashroyale.com/v1/'


def fetch_player_cr_data(gamer_tag):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {0}'.format(current_app.config['CLASH_ROYALE_TOKEN'])
    }

    api_url = '%splayers/%s' % (API_URL_BASE, urllib.parse.quote(gamer_tag))
    return requests.get(api_url, headers=headers)


def sync_cr_user_with_tag(user_id, gamer_tag, db=None):
    """Fetch data for a user from clash royale and update its data.

    Return True if we succeed to fetch the data, False otherwise.
    """
    response = fetch_player_cr_data(gamer_tag)
    if response.status_code == 200:
        json_response = json.loads(response.content.decode('utf-8'))
        if db is None:
            db = get_db()
        db.execute(
            'REPLACE INTO clash_royale_stats (user_id, wins, loses, trophies)'
            'VALUES (?, ?, ?, ?)',
            (user_id, json_response['wins'], json_response['losses'],
             json_response['trophies'])
        )
        db.commit()
        return True
    return False


@click.command('sync-clash-royale')
@with_appcontext
def fetch_stats_command():
    """Fetch data from Clash Royale API in order to store stats inside apps.

    Doing a command allow it to be called from a task periodically. Furthermore,
    this command could then be migrate to do each user one by one and just create
    a task by user to allow distribution.
    """
    db = get_db()
    c = db.cursor()
    c.execute('SELECT id, game1_tag FROM player WHERE game1_tag IS NOT NULL AND is_active <> 0')

    for row in c.fetchall():
        if sync_cr_user_with_tag(row[0], row[1], db):
            click.echo('Data successfully sync for user %d with gamer tag %s' % (row[0], row[1]))
        else:
            click.echo('Could not sync data for user %d with gamer tag %s' % (row[0], row[1]))


def init_app(app):
    app.cli.add_command(fetch_stats_command)
