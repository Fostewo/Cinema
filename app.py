import json
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data.db_session import global_init, create_session
from data.films import Film
from data.users import User
from films_api import films_blueprint
from users_api import users_blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

app.register_blueprint(films_blueprint)
app.register_blueprint(users_blueprint)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('films_list'))
    return redirect(url_for('auth'))


@app.route('/auth')
def auth():
    return render_template('auth.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        db_sess = create_session()
        user = db_sess.query(User).filter(User.email == email).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            flash('Вы успешно вошли в систему', 'success')
            return redirect(url_for('films_list'))
        else:
            flash('Неверный email или пароль', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('auth'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return redirect(url_for('register'))

        db_sess = create_session()

        if db_sess.query(User).filter(User.email == email).first():
            flash('Пользователь с таким email уже существует', 'danger')
            return redirect(url_for('register'))

        user = User(
            name=name,
            email=email,
            is_admin=False
        )
        user.set_password(password)

        db_sess.add(user)
        db_sess.commit()

        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/films')
@login_required
def films_list():
    db_sess = create_session()

    # Получаем параметры фильтрации
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

    # Получаем список всех жанров для фильтра
    genres = [film.genre for film in db_sess.query(Film.genre).distinct()]

    return render_template(
        'films.html',
        films=films,
        genres=genres,
        selected_genre=genre,
        selected_date=date,
        selected_rating=rating,
        today=datetime.now().date()
    )


@app.route('/film/<int:film_id>')
@login_required
def film_detail(film_id):
    db_sess = create_session()
    film = db_sess.query(Film).get(film_id)

    if not film:
        flash('Фильм не найден', 'danger')
        return redirect(url_for('films_list'))

    return render_template(
        'film_detail.html',
        film=film,
        today=datetime.now().date()
    )


@app.route('/add_film', methods=['GET', 'POST'])
@login_required
def add_film():
    if not current_user.is_admin:
        flash('У вас нет прав для добавления фильмов', 'danger')
        return redirect(url_for('films_list'))

    if request.method == 'POST':
        try:
            title = request.form.get('title')
            genre = request.form.get('genre')
            release_date = datetime.strptime(request.form.get('release_date'), '%Y-%m-%d').date()
            rating = float(request.form.get('rating'))
            trailer_url = request.form.get('trailer_url')
            theaters = request.form.get('theaters')

            try:
                json.loads(theaters)
            except json.JSONDecodeError:
                flash('Некорректный формат данных о кинотеатрах', 'danger')
                return redirect(url_for('add_film'))

            db_sess = create_session()

            film = Film(
                title=title,
                genre=genre,
                release_date=release_date,
                rating=rating,
                trailer_url=trailer_url,
                theaters=theaters
            )

            db_sess.add(film)
            db_sess.commit()

            flash('Фильм успешно добавлен', 'success')
            return redirect(url_for('films_list'))
        except Exception as e:
            flash(f'Ошибка при добавлении фильма: {str(e)}', 'danger')

    return render_template('add_film.html')


@app.route('/edit_film/<int:film_id>', methods=['GET', 'POST'])
@login_required
def edit_film(film_id):
    if not current_user.is_admin:
        flash('У вас нет прав для редактирования фильмов', 'danger')
        return redirect(url_for('films_list'))

    db_sess = create_session()
    film = db_sess.query(Film).get(film_id)

    if not film:
        flash('Фильм не найден', 'danger')
        return redirect(url_for('films_list'))

    if film.release_date >= datetime.now().date():
        flash('Редактирование возможно только после даты показа фильма', 'danger')
        return redirect(url_for('film_detail', film_id=film.id))

    if request.method == 'POST':
        try:
            film.title = request.form.get('title')
            film.genre = request.form.get('genre')
            film.release_date = datetime.strptime(request.form.get('release_date'), '%Y-%m-%d').date()
            film.rating = float(request.form.get('rating'))
            film.trailer_url = request.form.get('trailer_url')

            theaters = request.form.get('theaters')
            try:
                json.loads(theaters)
                film.theaters = theaters
            except json.JSONDecodeError:
                flash('Некорректный формат данных о кинотеатрах', 'danger')
                return redirect(url_for('edit_film', film_id=film.id))

            db_sess.commit()
            flash('Фильм успешно обновлен', 'success')
            return redirect(url_for('film_detail', film_id=film.id))
        except Exception as e:
            flash(f'Ошибка при обновлении фильма: {str(e)}', 'danger')

    return render_template('edit_film.html', film=film)


@app.route('/delete_film/<int:film_id>', methods=['POST'])
@login_required
def delete_film(film_id):
    if not current_user.is_admin:
        flash('У вас нет прав для удаления фильмов', 'danger')
        return redirect(url_for('films_list'))

    db_sess = create_session()
    film = db_sess.query(Film).get(film_id)

    if not film:
        flash('Фильм не найден', 'danger')
        return redirect(url_for('films_list'))

    if film.release_date >= datetime.now().date():
        flash('Удаление возможно только после даты показа фильма', 'danger')
        return redirect(url_for('film_detail', film_id=film.id))

    try:
        db_sess.delete(film)
        db_sess.commit()
        flash('Фильм успешно удален', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении фильма: {str(e)}', 'danger')

    return redirect(url_for('films_list'))


@app.route('/profile')
@login_required
def profile():
    return render_template('user_profile.html')


@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    name = request.form.get('name')
    email = request.form.get('email')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    db_sess = create_session()
    user = db_sess.query(User).get(current_user.id)

    if not user.check_password(current_password):
        flash('Неверный текущий пароль', 'danger')
        return redirect(url_for('profile'))

    if name:
        user.name = name
    if email:
        user.email = email
    if new_password:
        user.set_password(new_password)

    db_sess.commit()
    flash('Профиль успешно обновлен', 'success')
    return redirect(url_for('profile'))


def main():
    global_init("db/films_cinema.db")

    db_sess = create_session()
    if not db_sess.query(User).filter(User.email == 'admin@example.com').first():
        admin = User(
            name='Admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('admin')
        db_sess.add(admin)
        db_sess.commit()

    app.run(debug=True)


if __name__ == '__main__':
    main()
