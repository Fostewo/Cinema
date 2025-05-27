import json

import requests

BASE_URL = 'http://127.0.0.1:5000'


def format_response(status_code, message, data=None):
    response = {
        "status": "success" if status_code < 400 else "error",
        "code": status_code,
        "message": message,
    }
    if data is not None:
        response["data"] = data
    return json.dumps(response, indent=2)


def test_films():
    results = {"films": []}

    # Тест получения фильмов
    response = requests.get(f'{BASE_URL}/api/films')
    if response.status_code == 200:
        data = response.json()
        results["films"].append({
            "test": "GET /api/films",
            "status": "success",
            "films_count": len(data.get('films', []))
        })
    else:
        results["films"].append({
            "test": "GET /api/films",
            "status": "error",
            "error": response.text
        })

    # Тест создания фильма
    test_film = {
        'title': 'Test Film',
        'genre': 'Test Genre',
        'release_date': '2023-12-31',  # Фиксированная дата
        'rating': 8.5,
        'trailer_url': 'https://youtube.com/test',
        'theaters': '[{"name": "Test Theater", "lat": 55.75, "lon": 37.61}]'
    }
    response = requests.post(
        f'{BASE_URL}/api/films',
        json=test_film,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 201:
        data = response.json()
        film_id = data.get('film_id')
        results["films"].append({
            "test": "POST /api/films",
            "status": "success",
            "film_id": film_id
        })

        # Тест обновления фильма
        update_data = {
            'title': 'Updated Film',
            'rating': 9.0
        }
        response = requests.put(
            f'{BASE_URL}/api/films/{film_id}',
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            results["films"].append({
                "test": f"PUT /api/films/{film_id}",
                "status": "success",
                "updated_fields": update_data
            })
        else:
            results["films"].append({
                "test": f"PUT /api/films/{film_id}",
                "status": "error",
                "error": response.text
            })
    else:
        results["films"].append({
            "test": "POST /api/films",
            "status": "error",
            "error": response.text
        })

    return format_response(200, "Films tests completed", results)


def test_users():
    results = {"users": []}

    # Тест получения пользователей
    response = requests.get(f'{BASE_URL}/api/users')
    if response.status_code == 200:
        data = response.json()
        results["users"].append({
            "test": "GET /api/users",
            "status": "success",
            "users_count": len(data.get('users', []))
        })
    else:
        results["users"].append({
            "test": "GET /api/users",
            "status": "error",
            "error": response.text
        })

    # Тест создания пользователя
    test_user = {
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'test123'
    }
    response = requests.post(
        f'{BASE_URL}/api/users',
        json=test_user,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 201:
        data = response.json()
        user_id = data.get('user_id')
        results["users"].append({
            "test": "POST /api/users",
            "status": "success",
            "user_id": user_id
        })

        # Тест обновления пользователя
        update_data = {
            'name': 'Updated User',
            'email': 'updated@example.com'
        }
        response = requests.put(
            f'{BASE_URL}/api/users/{user_id}',
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            results["users"].append({
                "test": f"PUT /api/users/{user_id}",
                "status": "success",
                "updated_fields": update_data
            })
        else:
            results["users"].append({
                "test": f"PUT /api/users/{user_id}",
                "status": "error",
                "error": response.text
            })
    else:
        results["users"].append({
            "test": "POST /api/users",
            "status": "error",
            "error": response.text
        })

    return format_response(200, "Users tests completed", results)


if __name__ == '__main__':
    films_result = test_films()
    users_result = test_users()

    final_result = {
        "films_tests": json.loads(films_result),
        "users_tests": json.loads(users_result),
        "message": "All tests completed"
    }

    print(json.dumps(final_result, indent=2))
