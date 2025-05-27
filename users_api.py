from flask import Blueprint, jsonify, request

from data.db_session import create_session
from data.users import User

users_blueprint = Blueprint('users_api', __name__)


@users_blueprint.route('/api/users', methods=['GET'])
def get_users():
    db_sess = create_session()
    users = db_sess.query(User).all()
    return jsonify({
        'users': [{
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'is_admin': user.is_admin
        } for user in users]
    })


@users_blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db_sess = create_session()
    user = db_sess.query(User).get(user_id)

    if not user:
        return jsonify({'error': 'Not found'}), 404

    return jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'is_admin': user.is_admin
        }
    })


@users_blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({'error': 'Empty request'}), 400

    required_fields = ['name', 'email', 'password']
    if not all(field in request.json for field in required_fields):
        return jsonify({'error': 'Bad request'}), 400

    db_sess = create_session()

    if db_sess.query(User).filter(User.email == request.json['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    user = User(
        name=request.json['name'],
        email=request.json['email'],
        is_admin=request.json.get('is_admin', False)
    )
    user.set_password(request.json['password'])

    db_sess.add(user)
    db_sess.commit()

    return jsonify({
        'success': 'OK',
        'user_id': user.id
    }), 201


@users_blueprint.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if not request.json:
        return jsonify({'error': 'Empty request'}), 400

    db_sess = create_session()
    user = db_sess.query(User).get(user_id)

    if not user:
        return jsonify({'error': 'Not found'}), 404

    if 'name' in request.json:
        user.name = request.json['name']
    if 'email' in request.json:
        if db_sess.query(User).filter(User.email == request.json['email'], User.id != user_id).first():
            return jsonify({'error': 'Email already in use'}), 400
        user.email = request.json['email']
    if 'password' in request.json:
        user.set_password(request.json['password'])
    if 'is_admin' in request.json:
        user.is_admin = request.json['is_admin']

    db_sess.commit()
    return jsonify({'success': 'OK'})


@users_blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_sess = create_session()
    user = db_sess.query(User).get(user_id)

    if not user:
        return jsonify({'error': 'Not found'}), 404

    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})
