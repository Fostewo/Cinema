import json
from datetime import datetime

from flask import Blueprint, jsonify, request

from data.db_session import create_session
from data.films import Film

films_blueprint = Blueprint('films_api', __name__)


@films_blueprint.route('/api/films', methods=['GET'])
def get_films():
    db_sess = create_session()

    # Фильтрация
    genre = request.args.get('genre')
    date = request.args.get('date')
    rating = request.args.get('rating')

    query = db_sess.query(Film)

    if genre:
        query = query.filter(Film.genre == genre)
    if date:
        query = query.filter(Film.release_date == datetime.strptime(date, '%Y-%m-%d').date())
    if rating:
        query = query.filter(Film.rating >= float(rating))

    films = query.all()

    return jsonify({
        'films': [film.to_dict() for film in films]
    })


@films_blueprint.route('/api/films/<int:film_id>', methods=['GET'])
def get_film(film_id):
    db_sess = create_session()
    film = db_sess.query(Film).get(film_id)

    if not film:
        return jsonify({'error': 'Not found'}), 404

    return jsonify({
        'film': film.to_dict()
    })


@films_blueprint.route('/api/films', methods=['POST'])
def create_film():
    if not request.json:
        return jsonify({'error': 'Empty request'}), 400

    required_fields = ['title', 'genre', 'release_date', 'rating', 'trailer_url', 'theaters']
    if not all(field in request.json for field in required_fields):
        return jsonify({'error': 'Bad request'}), 400

    try:
        json.loads(request.json['theaters'])
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid theaters format'}), 400

    db_sess = create_session()

    film = Film(
        title=request.json['title'],
        genre=request.json['genre'],
        release_date=datetime.strptime(request.json['release_date'], '%Y-%m-%d').date(),
        rating=float(request.json['rating']),
        trailer_url=request.json['trailer_url'],
        theaters=request.json['theaters']
    )

    db_sess.add(film)
    db_sess.commit()

    return jsonify({'success': 'OK', 'film_id': film.id}), 201


@films_blueprint.route('/api/films/<int:film_id>', methods=['PUT'])
def update_film(film_id):
    if not request.json:
        return jsonify({'error': 'Empty request'}), 400

    db_sess = create_session()
    film = db_sess.query(Film).get(film_id)

    if not film:
        return jsonify({'error': 'Not found'}), 404

    if film.release_date >= datetime.now().date():
        return jsonify({'error': 'Editing is allowed only after release date'}), 403

    fields = ['title', 'genre', 'release_date', 'rating', 'trailer_url', 'theaters']
    for field in fields:
        if field in request.json:
            if field == 'release_date':
                setattr(film, field, datetime.strptime(request.json[field], '%Y-%m-%d').date())
            elif field == 'rating':
                setattr(film, field, float(request.json[field]))
            elif field == 'theaters':
                try:
                    json.loads(request.json[field])
                    setattr(film, field, request.json[field])
                except json.JSONDecodeError:
                    return jsonify({'error': 'Invalid theaters format'}), 400
            else:
                setattr(film, field, request.json[field])

    db_sess.commit()
    return jsonify({'success': 'OK'})


@films_blueprint.route('/api/films/<int:film_id>', methods=['DELETE'])
def delete_film(film_id):
    db_sess = create_session()
    film = db_sess.query(Film).get(film_id)

    if not film:
        return jsonify({'error': 'Not found'}), 404

    if film.release_date >= datetime.now().date():
        return jsonify({'error': 'Deletion is allowed only after release date'}), 403

    db_sess.delete(film)
    db_sess.commit()
    return jsonify({'success': 'OK'})
