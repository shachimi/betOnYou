import functools
import json

from flask import Blueprint, request

from .db import get_db
from .utils import fetch_player_data, sync_user_with_tag


blueprint = Blueprint('api', __name__, url_prefix='/api')


@blueprint.route('/players', methods=('GET',))
def retrieve_players():
    c = get_db().cursor()
    c.execute('select id, username, email, first_name, last_name from player where is_active = 1')

    return {'results': [
        {
            'id': row[0],
            'username': row[1],
            'email': row[2],
            'first_name': row[3],
            'last_name': row[4]
        }
        for row in c.fetchall()
    ]}


@blueprint.route('/game1/<username>', methods=('GET',))
def retrieve_player_game_data(username):
    c = get_db().cursor()
    c.execute(
        'select game1_tag from player where username = ?',
        (username, ),
    )

    row = c.fetchone()
    if row is None:
        return {}, 404
    if row[0] is None:
        return {'error': 'no player tag record for the given user'}, 400

    response = fetch_player_data(row[0])
    if response.status_code / 100 != 2:
        return {'error': 'unable to fetch player data, got %s error.' % response.status_code}

    return json.loads(response.content.decode('utf-8'))


@blueprint.route('/game1/<username>/refresh', methods=('POST',))
def refresh_player_game_data(username):
    c = get_db().cursor()
    c.execute(
        'select id, game1_tag from player where username = ?',
        (username, ),
    )

    row = c.fetchone()
    if row is None:
        return {}, 404
    if row[1] is None:
        return {'error': 'no player tag record for the given user'}, 400

    if not sync_user_with_tag(row[0], row[1]):
        return {'error': 'something went wrong when trying to refresh player data'}, 500
    return {}


@blueprint.route('/player/<username>', methods=('GET',))
def retrieve_player(username):
    c = get_db().cursor()
    c.execute(
        'select id, email, first_name, last_name, game1_username from player where username = ?',
        (username, ),
    )

    row = c.fetchone()
    if row is None:
        return {}, 404

    response = {
        'username': username,
        'email': row[1],
        'first_name': row[2],
        'last_name': row[3],
    }

    if row[4] is not None:
        response['clash_royale'] = {
            'username': row[4]
        }
        c = get_db().cursor()
        c.execute(
            'select wins, loses, trophies from clash_royale_stats where user_id = ?',
            (row[0], ),
        )
        row = c.fetchone()
        if row is not None:
            response['clash_royale'].update({
                'wins': row[0],
                'loses': row[1],
                'trophies': row[2]
            })

    return response


@blueprint.route('/add_player', methods=('POST',))
def add_player():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    db = get_db()
    error = None

    if not username or not email:
        error = 'Player needs username and email to be registered'

    if error is None:
        db.execute(
            'INSERT INTO player (username, email, first_name, last_name, is_active, '
            ' game1_username, game2_username, game1_tag) VALUES (?, ?, ?, ?, 1, ?, ?, ?)',
            (username, email, data.get('first_name'), data.get('last_name'),
             data.get('game1_username'), data.get('game2_username'), data.get('game1_tag'))
        )
        db.commit()
        return {}, 201

    return {'error': error}


@blueprint.route('/update_player/<username>', methods=('POST',))
def update_player(username):
    data = request.get_json()
    db = get_db()

    c = db.cursor()
    c.execute(
        'select id, game1_tag from player where username = ?',
        (username, ),
    )

    row = c.fetchone()
    if row is None:
        return {}, 404

    db.execute(
        'UPDATE player SET first_name = ?, last_name = ?,'
        ' game1_username = ?, game2_username = ?, game1_tag = ? WHERE username = ?',
        (data.get('first_name'), data.get('last_name'), data.get('game1_username'),
         data.get('game2_username'), data.get('game1_tag'), username)
    )
    db.commit()
    game1_tag = row[1] if data.get('game1_tag', None) is None else data.get('game1_tag')
    if game1_tag:
        sync_user_with_tag(row[0], game1_tag)
    return {}, 200



@blueprint.route('/delete_player/<username>', methods=('DELETE',))
def delete_player(username):
    db = get_db()
    c = db.cursor()
    c.execute(
        'select username from player where username = ?',
        (username, ),
    )

    row = c.fetchone()
    if row is None:
        return {}, 404

    c.execute('DELETE FROM player WHERE username = ?', (username,))
    db.commit()
    return {}
