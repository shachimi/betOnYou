import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    request,
    session,
    url_for,
)

from .db import get_db


blueprint = Blueprint('api', __name__, url_prefix='/api')


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


@blueprint.route('/player/<username>', methods=('GET',))
def retrieve_player(username):
    c = get_db().cursor()
    c.execute(
        'select username, email, first_name, last_name from player where username = ?',
        (username, ),
    )

    row = c.fetchone()
    if row is None:
        return {}, 404

    return {
        'username': row[0],
        'email': row[1],
        'first_name': row[2],
        'last_name': row[3]
    }


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
            ' game1_username, game2_username) VALUES (?, ?, ?, ?, 1, ?, ?)',
            (username, email, data.get('first_name'), data.get('last_name'),
             data.get('game1_username'), data.get('game2_username'))
        )
        print(db.commit())
        return {}, 201

    return {'error': error}


@blueprint.route('/update_player/<username>', methods=('POST',))
def update_player(username):
    data = request.get_json()
    db = get_db()

    c = db.cursor()
    c.execute(
        'select username from player where username = ?',
        (username, ),
    )

    row = c.fetchone()
    if row is None:
        return {}, 404

    db.execute(
        'UPDATE player SET first_name = ?, last_name = ?,'
        ' game1_username = ?, game2_username = ? WHERE username = ?',
        (data.get('first_name'), data.get('last_name'), data.get('game1_username'),
         data.get('game2_username'), username)
    )
    print(db.commit())
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
