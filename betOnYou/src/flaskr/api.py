import functools
import json

from flask import Blueprint, current_app, request

from flaskr.db import get_db
from flaskr.utils.cr_api import fetch_player_cr_data, sync_cr_user_with_tag
from flaskr.utils.fortnite_api import (
    fetch_player_fortnite_data,
    get_account_id_from_username,
    sync_fortnite_user_with_tag,
)


blueprint = Blueprint('api', __name__, url_prefix='/api')


def check_api_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False
    auth = auth_header.split(' ')
    # add a User/Secret table to log which user access the API in update mode
    return (
        len(auth) == 2 and
        auth[0].lower() == 'bearer' and
        auth[1] == current_app.config['API_SECRET']
    )


@blueprint.route('/players', methods=('GET',))
def retrieve_players():
    c = get_db().cursor()
    c.execute('select username, email, first_name, last_name from player where is_active = 1')

    return {'results': [
        {
            'username': row[0],
            'email': row[1],
            'first_name': row[2],
            'last_name': row[3]
        }
        for row in c.fetchall()
    ]}


@blueprint.route('/game1/<username>', methods=('GET',))
def retrieve_player_game_data(username):
    if not check_api_token(request):
        return {'error': 'Unauthorized'}, 401

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

    response = fetch_player_cr_data(row[0])
    if response.status_code / 100 != 2:
        return {'error': 'unable to fetch player data, got %s error.' % response.status_code}

    return json.loads(response.content.decode('utf-8'))


@blueprint.route('/game2/<username>', methods=('GET',))
def retrieve_player_fortnite_data(username):
    if not check_api_token(request):
        return {'error': 'Unauthorized'}, 401

    c = get_db().cursor()
    c.execute(
        'select game2_username, game2_tag from player where username = ?',
        (username, ),
    )

    row = c.fetchone()
    if row is None:
        return {}, 404
    if row[1] is None:
        if row[0] is None:
            return {'error': 'no player tag record for the given user'}, 400
        else:
            gamer_tag = get_account_id_from_username(row[0])
            if gamer_tag is None:
                return {'error': 'unable to retrieve gamer_tag using username'}, 400
    else:
        gamer_tag = row[1]

    response = fetch_player_fortnite_data(gamer_tag)
    if response.status_code / 100 != 2:
        return {'error': 'unable to fetch player data, got %s error.' % response.status_code}

    return json.loads(response.content.decode('utf-8'))


@blueprint.route('/game1/<username>/refresh', methods=('POST',))
def refresh_player_game_data(username):
    if not check_api_token(request):
        return {'error': 'Unauthorized'}, 401

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

    if not sync_cr_user_with_tag(row[0], row[1]):
        return {'error': 'something went wrong when trying to refresh player data'}, 500
    return {}


@blueprint.route('/game2/<username>/refresh', methods=('POST',))
def refresh_player_fortnite_data(username):
    if not check_api_token(request):
        return {'error': 'Unauthorized'}, 401

    c = get_db().cursor()
    c.execute(
        'select id, game2_username, game2_tag from player where username = ?',
        (username, ),
    )

    row = c.fetchone()
    if row is None:
        return {}, 404
    if row[2] is None:
        if row[1] is None:
            return {'error': 'no player tag record for the given user'}, 400
        else:
            gamer_tag = get_account_id_from_username(row[1])
            if gamer_tag is None:
                return {'error': 'unable to retrieve gamer_tag using username'}, 400
    else:
        gamer_tag = row[2]

    if not sync_fortnite_user_with_tag(row[0], gamer_tag):
        return {'error': 'something went wrong when trying to refresh player data'}, 500
    return {}


@blueprint.route('/player/<username>', methods=('GET',))
def retrieve_player(username):
    c = get_db().cursor()
    c.execute(
        'select id, email, first_name, last_name, game1_username, game2_username from'
        ' player where username = ?',
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
        cr_row = c.fetchone()
        if cr_row is not None:
            response['clash_royale'].update({
                'wins': cr_row[0],
                'loses': cr_row[1],
                'trophies': cr_row[2]
            })

    if row[5] is not None:
        response['fortnite'] = {
            'username': row[5]
        }
        c = get_db().cursor()
        c.execute(
            'select top1, kills, matchesplayed from fortnite_stats where user_id = ?',
            (row[0], ),
        )
        ft_row = c.fetchone()
        if ft_row is not None:
            response['fortnite'].update({
                'top1': ft_row[0],
                'kills': ft_row[1],
                'matches_played': ft_row[2]
            })


    return response


@blueprint.route('/add_player', methods=('POST',))
def add_player():
    if not check_api_token(request):
        return {'error': 'Unauthorized'}, 401

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
    if not check_api_token(request):
        return {'error': 'Unauthorized'}, 401

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
        ' game1_username = ?, game2_username = ?, game1_tag = ?, game2_tag = ? WHERE username = ?',
        (data.get('first_name'), data.get('last_name'), data.get('game1_username'),
         data.get('game2_username'), data.get('game1_tag'), data.get('game2_tag'), username)
    )
    db.commit()
    return {}, 200



@blueprint.route('/delete_player/<username>', methods=('DELETE',))
def delete_player(username):
    if not check_api_token(request):
        return {'error': 'Unauthorized'}, 401

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
